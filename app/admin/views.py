# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:12'
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, \
    PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, UserLog,\
    AdminLog, MovieFavorite, OperateLog, Auth, Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import uuid
import datetime
import os
from werkzeug.security import generate_password_hash



# 上下文处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decorate_func(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorate_func


# 修改文件名
def change_filename(filename):
    filepath = os.path.dirname(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + str(filepath)
    return filename


# index
@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


# admin登录
@admin.route("/login/", methods=["GET", "POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data["passwd"]):
            flash("密码错误", "Error")
            return redirect(url_for("admin.login"))

        # session用于登录装饰器时判断
        session["admin"] = data["account"]
        session["admin_id"] = admin.id

        # 管理员登录日志
        adminlogin_log = AdminLog(
            admin_id = admin.id,
            ip = request.remote_addr
        )

        db.session.add(adminlogin_log)
        db.session.commit()

        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# logout
@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 修改密码
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        admin.pwd = generate_password_hash(data["new_passwd"])

        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改密码"
        )

        db.session.add(operatelog)
        db.session.commit()
        redirect(url_for("admin.pwd"))
        return redirect(url_for("admin.logout"))
    return render_template("admin/passwd.html", form=form)


# 评论列表
@admin.route("/comments/list/", methods=["GET", "POST"])
@admin_login_req
def comments_list():
    page = int(request.args.get('page', '1', type=int))

    # query.join()
    page_num = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id,
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comments_list.html", page_num=page_num)


# 删除评论
@admin.route("/comments/del/<int:id>", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    comment = Comment.query.get_or_404(id)

    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功", "OK")
    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除评论：" + comment.content
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.comments_list", page=1))




# 添加电影
@admin.route("/movies_add", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        movies = Movie(
            title = data["title"],
            url = data["url"],
            description = data["info"],
            star = data["star"],
            logo = logo,
            tag_id = data["tag_id"],
            length = data["length"],
            area = data["area"],
            release_time = data["release_time"],
            play_num = 0,
            comment_num = 0
        )

        db.session.add(movies)
        db.session.commit()
        flash("添加电影成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加电影：" + data["title"]
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.movie_add"))

    return render_template("admin/movie_add.html", form=form)


# 电影列表
@admin.route("/movie_list/", methods=["GET","POST"])
@admin_login_req
def movie_list():
    page = int(request.args.get('page', '1', type=int))
    # page_data = Movie.query.all()
    page_num = Movie.query.paginate(page=page, per_page=10)

    return render_template("admin/movie_list.html", page_num=page_num)

# 删除电影
@admin.route("/movies/del/<int:id>/", methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))

    db.session.delete(movie)
    db.session.commit()

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除：" + movie.title
    )

    db.session.add(operatelog)
    db.session.commit()
    flash("删除电影成功", "OK")
    return redirect(url_for("admin.movie_list", page=1))


# 编辑电影
@admin.route("/movies/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.description
        form.star.data = movie.star
        form.tag_id.data = movie.tag_id

    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()

        # 判断电影是否修改为已存在的电影
        if movie_count == 1 and movie.title != data["title"]:
            flash("片名已存在", "Error")
            return redirect(url_for("admin.movie_edit", id=movie.id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")

        # 判断是否更改logo
        if form.logo.data:
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)


        movie.title = data["title"]
        movie.url = data["url"]
        movie.description = data["info"]
        movie.tag_id = data["tag_id"]
        movie.star = data["star"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]

        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改电影：" + str(movie.id)
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for('admin.movie_edit', id=movie.id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 电影收藏列表
@admin.route("/moviefav/list/", methods=["GET", "POST"])
@admin_login_req
def moviefav_list():
    page = int(request.args.get('page', '1', type=int))
    page_num = MovieFavorite.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == MovieFavorite.movie_id,
        User.id == MovieFavorite.user_id,
    ).order_by(
        MovieFavorite.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/moviefav_list.html", page_num=page_num)


# 电影收藏删除
@admin.route("/moviefav/del/<int:id>", methods=["GET"])
@admin_login_req
def moviefav_del(id=None):
    moviefav = MovieFavorite.query.get_or_404(id)

    db.session.delete(moviefav)
    db.session.commit()
    flash("删除电影收藏", "OK")
    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除电影收藏：" + str(moviefav.movie_id)
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.moviefav_list", page=1))


# 添加预告片
@admin.route("/preview_add/", methods=["GET", "POST"])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo )
        preview = Preview(
            title = data["title"],
            logo = logo,
        )

        db.session.add(preview)
        db.session.commit()
        flash("添加预告片成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加预告片：" + data["title"]
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.preview_add"))

    return render_template("admin/preview_add.html", form=form)


# 预告片列表
@admin.route("/preview/list/", methods=["GET", "POST"])
@admin_login_req
def preview_list():
    page = int(request.args.get('page', '1', type=int))
    page_num = Preview.query.order_by(Preview.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_num=page_num)


# 编辑预告片
@admin.route("/preview/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    form.logo.validators = []
    preview = Preview.query.get_or_404(id)

    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview_count == 1 and preview.title != data["title"]:
            flash("预告片已存在", "Error")
            return redirect("admin.preview_edit")

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")

        if form.logo.data:
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)

        preview.title = data["title"]

        db.session.add(preview)
        db.session.commit()
        flash("修改预告片成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改预告片：" + str(preview.id)
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.preview_edit", id=preview.id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 删除预告片
@admin.route("/preview/del/<int:id>", methods=["GET"])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.get_or_404(id)

    db.session.delete(preview)
    db.session.commit()
    flash("删除预告片成功", "OK")

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除预告片：" + preview.title
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.preview_list", page=1))


# 标签添加
@admin.route("/tag/add/", methods=["GET", "POST"])
@admin_login_req
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()

        # 检查是否已存在输入的标签
        if tag == 1:
            flash("标签已存在！", "Error")
            return redirect(url_for("admin.tag_add"))

        # 标签入库
        tag = Tag(
            name = data["name"],
        )

        db.session.add(tag)
        db.session.commit()
        flash("标签添加成功", "OK")
        operatelog = OperateLog(
            admin_id = session["admin_id"],
            ip = request.remote_addr,
            reason = "添加标签：" + data["name"]
        )

        db.session.add(operatelog)
        db.session.commit()

        redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 标签列表
@admin.route("/tag/list/", methods=["GET", "POST"])
@admin_login_req
def tag_list(page=None):
    page = int(request.args.get('page', '1', type=int))
    page_num = Tag.query.order_by(Tag.add_time.desc()).paginate(page=page, per_page=10)

    return render_template("admin/tag_list.html", page_num=page_num)

# 标签删除
@admin.route("/tag/del/<int:id>/", methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()

    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功", "OK")

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除标签：" + tag.name
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.tag_list", page=1))


# 编辑标签
@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def tag_edit(id=None):
    tag = Tag.query.get_or_404(id)
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag_count == 1 and tag.name != data["name"]:
            flash("标签已经存在", "Error")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data["name"]

        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改标签：" + str(tag.id)
        )

        db.session.add(operatelog)
        db.session.commit()
        redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 用户列表
@admin.route("/user/list/", methods=["GET", "POST"])
@admin_login_req
def user_list(page=None):
    page = int(request.args.get('page', '1', type=int))
    page_num = User.query.order_by(User.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_num=page_num)


# 查看用户主页
@admin.route("/user/view/<int:id>")
@admin_login_req
def user_view(id=None):
    user = User.query.get_or_404(id)
    return render_template("admin/user_view.html", user=user)


# 删除用户
@admin.route("/user/del/<int:id>", methods=["GET"])
@admin_login_req
def user_del(id=None):
    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()
    flash("删除用户成功", "OK")

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除用户：" + user.name
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.user_list", page=1))


# 操作日志列表
@admin.route("/oplog/list/", methods=["GET", "POST"])
@admin_login_req
def oplog_list():
    page = int(request.args.get('page', '1', type=int))
    page_num = OperateLog.query.join(
        Admin
    ).filter(
       Admin.id == OperateLog.admin_id,
    ).order_by(
        OperateLog.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/oplog_list.html", page_num=page_num)


# 管理员登录日志
@admin.route("/adminloginlog/list/", methods=["GET", "POST"])
@admin_login_req
def adminloginlog_list(page=None):
    page = int(request.args.get('page', '1', type=int))
    page_num = AdminLog.query.join(
        Admin
    ).filter(
        Admin.id == AdminLog.admin_id
    ).order_by(
        AdminLog.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/adminloginlog_list.html", page_num=page_num)


# 用户登录日志列表
@admin.route("/userloginlog/list/", methods=["GET", "POST"])
@admin_login_req
def userloginlog_list(page=None):
    page = int(request.args.get('page', '1', type=int))
    page_num = UserLog.query.join(
        User
    ).filter(
        User.id == UserLog.user_id,
    ).order_by(
        UserLog.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/userloginlog_list.html", page_num=page_num)


# 添加权限
@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth_count = Auth.query.filter_by(name=data["name"]).count()
        if auth_count == 1:
            flash("权限名称已存在", "Error")
            return redirect(url_for("admin.auth_add"))
        auth = Auth(
            name = data["name"],
            url = data["url"]
        )

        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加权限：" + data["name"]
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html", form=form)


# 权限列表
@admin.route("/auth/list/", methods=["GET", "POST"])
@admin_login_req
def auth_list():
    page = int(request.args.get('page', '1', type=int))
    page_num = Auth.query.order_by(Auth.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html", page_num=page_num)


#　编辑权限
@admin.route("/auth/edit/<int:id>", methods=["GET", "POST"])
@admin_login_req
def auth_edit(id=None):
    form = AuthForm()
    auth = Auth.query.get_or_404(id)
    if request.method == "GET":
        form.name.data = auth.name
        form.url.data = auth.url

    if form.validate_on_submit():
        data = form.data
        auth_count = Auth.query.filter_by(name=data["name"]).count()
        if auth_count == 1 and auth.name != data["name"]:
            flash("权限名称已存在", "Error")
            return redirect(url_for("admin.auth_edit", id=id))

        auth.name = data["name"]
        auth.url = data["url"]

        db.session.add(auth)
        db.session.commit()
        flash("修改权限成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="修改权限：" + str(auth.id)
        )

        db.session.add(operatelog)
        db.session.commit()
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 删除权限
@admin.route("/auth/del/<int:id>", methods=["GET"])
@admin_login_req
def auth_del(id=None):
    auth = Auth.query.get_or_404(id)

    db.session.delete(auth)
    db.session.commit()
    flash("删除权限成功", "OK")

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除权限：" + auth.name
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.auth_list", page=1))


# 添加角色
@admin.route("/role/add", methods=["GET", "POST"])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role_count = Role.query.filter_by(name=data["name"]).count()
        if role_count:
            flash("角色已存在", "Error")
            return redirect(url_for("admin.role_add"))
        role = Role(
            name = data["name"],
            auths = ','.join(map(lambda x: str(x), data["auths"]))
        )

        db.session.add(role)
        db.session.commit()
        flash("添加角色成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加角色：" + data["name"]
        )

        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.role_list", page=1))
    return render_template("admin/role_add.html", form=form)


# 角色列表
@admin.route("/role/list/", methods=["GET", "POST"])
@admin_login_req
def role_list(page=None):
    page = int(request.args.get('page', '1', type=int))
    page_num = Role.query.order_by(Role.add_time.desc()).paginate(page=page, per_page=10)

    return render_template("admin/role_list.html", page_num=page_num)


# 角色删除
@admin.route("/role/del/<int:id>", methods=["GET"])
@admin_login_req
def role_del(id=None):
    role = Role.query.get_or_404(id)

    db.session.delete(role)
    db.session.commit()
    flash("删除角色", "OK")

    # 添加操作日志
    operatelog = OperateLog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除角色：" + role.name
    )

    db.session.add(operatelog)
    db.session.commit()
    return redirect(url_for("admin.role_list", page=1))


# 添加管理员
@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_req
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        admin_count = Admin.query.filter_by(name=data["name"]).count()
        if admin_count:
            flash("管理员已存在", "Error")
            return redirect(url_for("admin.admin_list", page=1))

        admin = Admin(
            name =  data["name"],
            pwd = generate_password_hash(data["pwd"]),
            role_id = data["role_id"],
            is_super = "1"
        )

        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功", "OK")

        # 添加操作日志
        operatelog = OperateLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加管理员：" + data["name"]
        )


        db.session.add(operatelog)
        db.session.commit()
        return redirect(url_for("admin.admin_list", page=1))
    return render_template("admin/admin_add.html", form=form)


# 管理员列表
@admin.route("/admin/list/", methods=["GET", "POST"])
@admin_login_req
def admin_list():
    page = int(request.args.get('page', '1', type=int))
    page_num = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(Admin.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/admin_list.html", page_num=page_num)

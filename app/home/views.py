# -*- coding: utf-8 -*-
__author__ = 'alan'
__date__ = '18-3-25 上午10:11'
from . import home
from flask import render_template, url_for, redirect, flash, request, session
from app.home.forms import RegisterForm, LoginForm, UserForm, PwdForm, CommentForm
from app.models import User, UserLog, Comment, Movie, Preview, Tag, MovieFavorite, Uncensored
from app import db
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import uuid
from functools import wraps
from app import *
import os
import datetime


# 修改文件名
def change_filename(filename):
    file_path = os.path.dirname(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + file_path
    return filename


# 会员登录装饰器
def user_login_rep(f):
    @wraps(f)
    def decorate_func(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorate_func



@home.route("/", methods=["GET", "POST"])
def index():
    page = int(request.args.get('page', '1', type=int))

    tags = Tag().query.order_by(Tag.add_time.desc())
    page_data = Movie.query.order_by(Movie.add_time.desc())

    # 标签
    tid = request.args.get("tid", 0, type=int)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))

    # 星级
    star = request.args.get("star", 0, type=int)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))

    # 时间
    time = request.args.get("time", 0, type=int)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.add_time.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.add_time.asc()
            )

    # 播放数量
    play_num = request.args.get("play_num", 0, type=int)
    if int(play_num) != 0:
        if int(play_num) == 1:
            page_data = page_data.order_by(
                Movie.play_num.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.play_num.asc()
            )

    # 评论量
    comment_num = request.args.get("comment_num", 0, type=int)
    if int(comment_num) != 0:
        if int(comment_num) == 1:
            page_data = page_data.order_by(
            Movie.comment_num.asc()
            )
        else:
            page_data = page_data.order_by(
                Movie.comment_num.desc()
            )

    page_data = page_data.paginate(page=page, per_page=24)
    t = dict(
        tid=tid,
        star=star,
        time=time,
        play_num=play_num,
        comment_num=comment_num
    )
    if sum(list(t.values())):
        query = "?tid=" + str(tid) + "&star=" + str(star) + "&time=" + str(time) + "&play_num=" + str(play_num) + "&comment_num=" + str(comment_num)
    else:
        query = request.args.get('query', '')
    return render_template("home/index.html", tags=tags, t=t, page_data=page_data, query=query)


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter((User.name==data["account"]) | (User.email==data["account"]) | (User.phone==data["account"])).first()
        if not user.check_pwd(data["passwd"]):
            flash("密码错误", "Error")
            return redirect(url_for("home.login"))
        session["user"] = user.name
        session["user_id"] = user.id

        # 会员登录日志
        user_log = UserLog(
            user_id=user.id,
            ip=request.remote_addr,
        )

        db.session.add(user_log)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.index"))
    return render_template("home/login.html", form=form)


@home.route("/logout/")
@user_login_rep
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data

        user = User(
            name = data["name"],
            email = data["email"],
            phone = data["phone"],
            pwd = generate_password_hash(data["pwd"]),
            uuid = uuid.uuid4().hex,
            add_time = datetime.datetime.now()
        )

        db.session.add(user)
        db.session.commit()
        flash("注册成功^_^, 请登录", "OK")
        return redirect(url_for("home.login"))

    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_rep
def user():
    form = UserForm()
    user = User.query.get(session["user_id"])
    form.img.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info

    if form.validate_on_submit():
        data = form.data
        name_count = User.query.filter_by(name=data["name"]).count()
        if name_count and user.name != data["name"]:
            flash("用户名已存在", "Error")

        email_count = User.query.filter_by(email=data["email"]).count()
        if email_count and user.email != data["email"]:
            flash("邮箱已存在", "Error")

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if phone_count and user.phone != data["phone"]:
            flash("手机号码已存在", "Error")

        if not os.path.exists(app.config["IMG_DIR"]):
            os.makedirs(app.config["IMG_DIR"])
            os.chmod(app.config["IMG_DIR"], "rw")

        if form.img.data:
            img_filename = secure_filename(form.img.data.filename)
            user.img = change_filename(img_filename)
            form.img.data.save(app.config["IMG_DIR"] + user.img )

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("个人资料修改成功", "OK")
        return redirect(url_for("home.user"))

    return render_template("home/user.html", form=form, user=user)


@home.route("/passwd", methods=["GET", "POST"])
@user_login_rep
def passwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        user.pwd = generate_password_hash(data["new_passwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功, 请重新登录", "OK")
        return redirect(url_for("home.logout"))

    return render_template("home/passwd.html", form=form)


@home.route("/loginlog/<int:page>", methods=["GET"])
@user_login_rep
def loginlog(page=None):
    if page is None:
        page = 1
    page_num = UserLog.query.filter(
        session["user_id"] == UserLog.user_id
    ).order_by(
        UserLog.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/loginlog.html", page_num=page_num)


@home.route("/comments/<int:page>/", methods=["GET"])
@user_login_rep
def comment_list(page=None):
    if page is None:
        page = 1
    page_num = Comment.query.join(
        User
    ).join(
        Movie
    ).filter(
        Comment.user_id == session["user_id"]
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/comments.html", page_num=page_num)


@home.route("/moviefav/add/", methods=["GET"])
@user_login_rep
def moviefav():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviefav = MovieFavorite.query.filter_by(
        user_id = int(uid),
        movie_id = int(mid),
    ).count()
    if moviefav == 1:
        data = dict(ok=0)
    if moviefav == 0:
        moviefav = MovieFavorite(
            user_id = int(uid),
            movie_id = int(mid),
        )
        db.session.add(moviefav)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@home.route("/search/<int:page>/", methods=["GET"])
def search(page=None):
    # page = int(request.args.get('page', '1', type=int))
    if page is None:
        page = 1
    key = request.args.get("key", "")

    movie_count = Movie.query.filter(
        Movie.area.ilike('%' + key + '%')
    ).count()

    page_data = Movie.query.filter(
        Movie.area.ilike('%' + key + '%'),
        Movie.title.ilike('%' + key + '%')
    ).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template("home/search.html", key=key, page_data=page_data, movie_count=movie_count)


@home.route("/play/<int:id>/<int:page>/", methods=["GET", "POST"])
@user_login_rep
def play(id=None, page=None):
    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_num = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(Comment.add_time.desc()).paginate(page=page, per_page=10)

    # 播放量
    movie.play_num = int(movie.play_num) + 1
    movie = db.session.merge(movie)
    db.session.add(movie)
    db.session.commit()

    #　评论量
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content = data["content"],
            movie_id = movie.id,
            user_id = session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()

        movie.comment_num = int(movie.comment_num) + 1
        db.session.add(movie)
        db.session.commit()
        flash("评论成功","OK")
        return redirect(url_for("home.play", id=movie.id, page=1))

    return render_template("home/play1.html", movie=movie, form=form, page_num=page_num)


@home.route("/animation/", methods=["GET"])
def animation():
    prev = Preview.query.all()
    return render_template("home/animation.html", prev=prev)


@home.route("/moviefav_list/<int:page>/", methods=["GET"])
@user_login_rep
def moviefav_list(page=None):
    if page is None:
        page = 1
    page_num = MovieFavorite.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == MovieFavorite.movie_id,
        User.id == session["user_id"]
    ).order_by(
        MovieFavorite.add_time.desc()
    ).paginate(page=page, per_page=10)

    # page_num = MovieFavorite.query.join(
    #     Uncensored
    # ).join(
    #     User
    # ).filter(
    #     Uncensored.id == MovieFavorite.uncensored_id,
    #     User.id == session["user_id"]
    # )

    return render_template("home/moviefav.html", page_num=page_num)


@home.route("/models/<string:name>/<int:page>/", methods=["GET"])
@user_login_rep
def models(name=None, page=None):
    if page is None:
        page = 1

    page_data = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.area == str(name)
    ).order_by(Movie.add_time.desc()).paginate(page=page, per_page=20)
    return render_template("home/models.html", page_data=page_data, name=name)


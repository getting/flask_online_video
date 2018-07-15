# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:12'
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role

tags_list = Tag.query.all()
auths_list = Auth.query.all()
roles_list = Role.query.all()


class LoginForm(FlaskForm):
    """管理员登录表单"""
    account = StringField(
        label='账号',
        validators=[DataRequired("请输入账号")],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            # "required": "required"
        }
    )

    passwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码")],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            # "required": "required"
        }
    )

    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-success  btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在")


class TagForm(FlaskForm):
    """标签管理表单"""
    name = StringField(
        label="标签",
        validators=[DataRequired("请输入标签！")],
        description="标签",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary",
        }
    )


class MovieForm(FlaskForm):
    """电影管理表单"""
    tags_list = Tag.query.all()
    title = StringField(
        label="片名",
        validators=[DataRequired("请输入片名")],
        description="片名",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！"
        }
    )

    url = StringField(
        label="链接",
        validators=[
            DataRequired("拷贝电影链接到这里")
        ],
        description="电影链接",
        render_kw={
            "class": "form-control",
            "placeholder": "拷贝电影链接到这里"
        }
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("输入电影简介")
        ],
        render_kw={
            "class": "form-control",
            "rows": "10",
            "id": "input_info",
            "placeholder": "请输入电影简介"
        }
    )

    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面")
        ],
        description="封面",
    )

    star = SelectField(
        label="评分",
        validators=[
            DataRequired("请选择星级")
        ],
        description="评分",
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        render_kw={
            "class": "form-control",
            "id": "input_star",
        }
    )

    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签id")
        ],
        description="标签id",
        coerce=int,
        choices=[(t.id, t.name) for t in tags_list],
        render_kw={
            "class": "form-control",
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
            "id": "input_area",
            "placeholder": "请输入地区！"
        }
    )

    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长！",

        }
    )

    release_time = StringField(
        label="发售时间",
        validators=[
            DataRequired("请输入发售时间")
        ],
        description="发售时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入发售时间！",
            "id": "input_release_time"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[DataRequired("请输入片名")],
        description="片名",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！"
        }
    )

    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面")
        ],
        description="封面",
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PwdForm(FlaskForm):
    old_passwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )

    new_passwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }

    )

    submit = SubmitField(
        label="提交",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    # 自定义检查旧密码
    def validate_old_passwd(self, field):
        from flask import session
        passwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(
            name = name
        ).first()
        if not admin.check_pwd(passwd):
            raise ValidationError("旧密码错误")


class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        validators=[DataRequired("请输入权限名称！")],
        description="权限名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入权限名称！"
        }
    )

    url = StringField(
        label="权限地址",
        validators=[DataRequired("请输入权限地址！")],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入权限地址！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary",
        }
    )


class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称",
        validators=[DataRequired("请输入角色名称！")],
        description="角色名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入角色名称！"
        }
    )

    auths = SelectMultipleField(
        label="权限列表",
        validators=[
            DataRequired("请选择权限")
        ],
        description="权限列表",
        coerce=int,
        choices=[(t.id, t.name) for t in auths_list],
        render_kw={
            "class": "form-control",
        }
    )

    submit = SubmitField(
        label="提交",
        render_kw={
            "class": "btn btn-primary "
        }
    )


class AdminForm(FlaskForm):
    name = StringField(
        label="管理员名称",
        validators=[DataRequired("请输入管理员名称！")],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入管理员名称！"
        }
    )

    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("请输入管理员密码")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！",
        }
    )

    re_pwd = PasswordField(
        label="重复输入管理员密码",
        validators=[
            DataRequired("请重复输入管理员密码"),
            EqualTo("pwd", message="两次密码不一致"),
        ],
        description="重复输入管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请重复输入管理员密码！",
        }
    )

    role_id = SelectField(
        label="所属角色id",
        validators=[
            DataRequired("请选择所属角色id")
        ],
        description="所属角色id",
        coerce=int,
        choices=[(t.id, t.name) for t in roles_list],
        render_kw={
            "class": "form-control",
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary",
        }
    )

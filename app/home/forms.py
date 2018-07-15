# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:11'
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Regexp
from app.models import User
from flask import session


class RegisterForm(FlaskForm):
    name = StringField(
        label="用户名",
        validators=[DataRequired("请输入用户名")],
        description="用户名",
        render_kw={
            "id": "input_name",
            "class": "form-control input-lg",
            "placeholder": "用户名"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱地址"),
            Email("邮箱地址不正确")
        ],
        description="邮箱地址",
        render_kw={
            "id": "input_email",
            "class": "form-control input-lg",
            "placeholder": "邮箱地址"
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号码"),
            Regexp("^(13[0-9]|14[57]|15[012356789]|17[678]|18[0-9])\\d{8}$", message="手机格式不正确")
        ],
        description="手机号码",
        render_kw={
            "id": "input_phone",
            "class": "form-control input-lg",
            "placeholder": "手机号码"
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码")],
        description="密码",
        render_kw={
            "id": "input_password",
            "class": "form-control input-lg",
            "placeholder": "密码"
        }
    )

    re_pwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请重新输入密码"),
            EqualTo("pwd", message="两次密码不一致")
        ],
        description="确认密码",
        render_kw={
            "id": "input_repassword",
            "class": "form-control input-lg",
            "placeholder": "确认密码"
        }
    )

    submit = SubmitField(
        label="注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

    def validate_name(self, field):
        name = field.data
        if User.query.filter_by(name=name).count():
            raise ValidationError("用户名已存在")

    def validate_email(self, field):
        email = field.data
        if User.query.filter_by(name=email).count():
            raise ValidationError("邮箱已存在")

    def validate_phone(self, field):
        phone = field.data
        if User.query.filter_by(name=phone).count():
            raise ValidationError("手机号码已存在")


class LoginForm(FlaskForm):
    """用户登录表单"""
    account = StringField(
        label='账号',
        validators=[
            DataRequired("请输入邮箱账号/用户名/手机号码"),
        ],
        description="账号",
        render_kw={
            "id": "input_name",
            "class": "form-control input-lg",
            "placeholder": "邮箱/用户名/手机号码"
        }
    )

    passwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码")],
        description="密码",
        render_kw={
            "id": "input_name",
            "class": "form-control input-lg",
            "placeholder": "密码"
        }
    )

    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_account(self, field):
        account = field.data
        user = User.query.filter((User.name == account) | (User.email == account) | (User.phone == account)).first()
        if not user:
            raise ValidationError("账号不存在")


class UserForm(FlaskForm):
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("请输入用户名")
        ],
        description="用户名",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入用户名"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱地址"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱地址"
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号码"),
            Regexp("^(13[0-9]|14[57]|15[012356789]|17[678]|18[0-9])\\d{8}$", message="手机格式不正确")
        ],
        description="手机号码",
        render_kw={
            "id": "input_phone",
            "class": "form-control input-lg",
            "placeholder": "手机号码"
        }
    )

    img = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像"),
        ],
        description="头像",
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )

    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success",
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
        '确认修改',
        render_kw={
            "class": "btn btn-success"
        }
    )

    def validate_old_passwd(self, field):
        passwd = field.data
        name = session["user"]
        user = User.query.filter_by(name=name).first()
        if not user.check_pwd(passwd):
            raise ValidationError("旧密码错误")


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入评论")
        ],
        description="内容",
        render_kw={
            "id": "input_content"
        }
    )

    submit = SubmitField(
        '提交评论',
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )


# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime, timedelta
import bcrypt
import concurrent.futures
from tornado import gen
import tornado.web
import wtforms
from wtforms_tornado import Form
import tornado.escape
from .base import BaseHandler
from fancy.models.invitation import Invitation
from fancy.models.auth import Auth, Active
from utils.mail import send_active_mail

logger = logging.getLogger(__name__)

# A thread pool to be used for password hashing with bcrypt.
executor = concurrent.futures.ThreadPoolExecutor(2)


class RegisterForm(Form):
    email = wtforms.TextField('email', validators=[wtforms.validators.Email(),
                              wtforms.validators.DataRequired()])
    username = wtforms.TextField('username',
                                 [wtforms.validators.Length(min=3, max=25),
                                  wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        validators=[wtforms.validators.Required()])


class LoginForm(Form):
    email = wtforms.TextField('email', validators=[wtforms.validators.Email(),
                              wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        validators=[wtforms.validators.Required()])


class VerifyInvitationHandler(BaseHandler):

    def initialize(self):
        super(VerifyInvitationHandler, self).initialize()
        self.model = Invitation

    def get(self):
        self.render("register_invitation.html", error=None)

    def post(self):
        invitation_code = self.get_argument("invitation_code", None)
        logger.info("invitation_code: " + invitation_code)
        try:
            self.model.get(self.model.code == invitation_code,
                           self.model.is_valid == True)
            self.write("hello")
        except self.model.DoesNotExist:
            self.write("sorry")


class RegisterHandler(BaseHandler):

    def initialize(self):
        super(RegisterHandler, self).initialize()
        self.model = Auth

    def get(self):
        self.render('register.html', error=None)

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        form = RegisterForm(self.request.arguments)
        if form.validate():
            email = self.get_argument("email")
            username = self.get_argument('username')
            hashed_password = yield executor.submit(
                bcrypt.hashpw,
                tornado.escape.utf8(self.get_argument("password")),
                bcrypt.gensalt())
            try:
                self.model.get(self.model.email == email)
                self.render('register.html', error="邮箱已注册")
            except self.model.DoesNotExist:
                user = self.model(email=email,
                                  username=username,
                                  password=hashed_password,
                                  last_login=datetime.now())
                user.save()
                self._need_active(user)
                self.redirect("/login")
        else:
            self.write(form.errors)
            self.set_status(400)

    def _need_active(self, user):
        time_expired = datetime.now() + timedelta(days=1)
        active = Active(uuid=uuid.NAMESPACE_URL,
                        user=user, time_expired=time_expired)
        active.save()
        send_active_mail(user, active.uuid, mail='sendcloud')


class LoginHandler(BaseHandler):
    """登录处理
    """

    def initialize(self):
        super(LoginHandler, self).initialize()
        self.model = Auth

    def get(self):
        self.render("login.html", error=None)

    @gen.coroutine
    def post(self):
        form = LoginForm(self.request.arguments)
        if form.validate():
            email = self.get_argument('email')
            passwd = self.get_argument('password')
            try:
                user = self.model.get(self.model.email == email)
                hashed_passwd = yield executor.submit(
                    bcrypt.hashpw, tornado.escape.utf8(passwd),
                    tornado.escape.utf8(user.password))
                if hashed_passwd == user.password:
                    self.set_secure_cookie("fancy_user", str(user.id))
                    self.redirect("/")
                else:
                    logger.info(u"密码错误")
                    raise self.model.DoesNotExist()
            except self.model.DoesNotExist:
                logger.info(u"登录失败")
                self.set_status(400)
                self.render("login.html", error="incorrect password")
        else:
            self.write(form.errors)
            self.set_status(400)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("fancy_user")
        self.redirect(self.get_argument("next", "/"))

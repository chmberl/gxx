# -*- coding: utf-8 -*-

import logging
import bcrypt
import concurrent.futures
import uuid
from tornado import gen
import tornado.escape
import wtforms
from wtforms_tornado import Form
from datetime import datetime, timedelta
from .base import BaseHandler
from fancy.models.invitation import Invitation
from fancy.models.auth import Auth, Active
from utils.mail import send_active_mail


logger = logging.getLogger(__name__)

executor = concurrent.futures.ThreadPoolExecutor(2)


class RegisterForm(Form):
    email = wtforms.TextField('email', validators=[wtforms.validators.Email(),
                              wtforms.validators.DataRequired()])
    username = wtforms.TextField('username',
                                 [wtforms.validators.Length(min=4, max=25),
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
                yield self._need_active(user)
                self.redirect("/login")
        else:
            self.set_status(400)

    def _need_active(self, user):
        time_expired = datetime.now() + timedelta(days=1)
        active = Active(uuid=uuid.NAMESPACE_URL,
                        user=user, time_expired=time_expired)
        send_active_mail(user, active.uuid, mail='sendcloud')

# -*- coding: utf-8 -*-

from fancy.handlers import (VerifyInvitationHandler, RegisterHandler,
                            LoginHandler, IndexHandler,
                            LogoutHandler)


urls = [
    ('/register_invitation', VerifyInvitationHandler, dict()),
    (r'/register', RegisterHandler, dict()),
    (r'/login', LoginHandler, dict()),
    (r'/logout', LogoutHandler, dict()),
    (r'/', IndexHandler, dict()),
]

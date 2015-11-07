# -*- coding: utf-8 -*-

import tornado.web
import config


class PeeweeHandler(tornado.web.RequestHandler):
    def prepare(self):
        config.database_none.connect()
        return super(PeeweeHandler, self).prepare()

    def on_finish(self):
        if not config.database_none.is_closed():
            config.database_none.close()
        return super(PeeweeHandler, self).on_finish()


class BaseHandler(PeeweeHandler):
    def get_current_user(self):
        return self.get_secure_cookie("fancy_user")

# -*- coding: utf-8 -*-

import os.path
import tornado.web
from urls import urls
import config


BASE_DIR = os.path.join(os.path.dirname(__file__))


def location(x):
    return os.path.join(BASE_DIR, x)


setting = dict(
    template_path=location("templates"),
    static_path=location("static"),
    xsrf_cookies=True,
    cookie_secret=config.COOKIE_SECRET,
    login_url='/register',
)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = urls
        settings = setting
        super(Application, self).__init__(handlers, **settings)


if __name__ == '__main__':
    pass

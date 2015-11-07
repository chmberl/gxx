# -*- coding: utf-8 -*-

import tornado.web
from .base import BaseHandler


class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("index.html", error=None)

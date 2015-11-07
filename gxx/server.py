# -*- coding: utf-8 -*-

import tornado.options
import tornado.ioloop
import tornado.autoreload
import config
import initial
from application import Application

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("db_name", default="zgxx_db", help="storm config for database")
define("db_user", default="gxx_dbuser", help=u"数据库登录名")
define("db_password", default="Y64eXDUcLE6HcpqW", help=u"数据库登录密码")
define("db_host", default="127.0.0.1", help=u"数据库服务器地址")
define("db_port", default=5432, help=u"数据库服务器端口", type=int)


config.database_none.init(options.db_name,
                          user=options.db_user,
                          password=options.db_password,
                          host=options.db_host,
                          port=options.db_port)
config.database_none.autorollback = True

if __name__ == '__main__':
    tornado.options.parse_command_line()
    initial.create_tables()
    application = Application()
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

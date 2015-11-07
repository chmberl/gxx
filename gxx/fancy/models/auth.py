# -*- coding: utf-8 -*-

import datetime
import peewee
import config


class Auth(peewee.Model):
    """登录信息
    """
    email = peewee.CharField(max_length=50)
    username = peewee.CharField(max_length=30)
    password = peewee.CharField(max_length=128)
    is_active = peewee.BooleanField(default=False)
    last_login = peewee.DateTimeField(null=True)
    date_joined = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.database_none
        db_table = "t_auth"


class Active(peewee.Model):
    """激活信息
    """
    uuid = peewee.UUIDField(index=True)
    user = peewee.ForeignKeyField(Auth, related_name="active")
    time_expired = peewee.DateTimeField()

    class Meta:
        database = config.database_none
        db_table = "t_auth_active"

# class Profile(peewee.Model):
#     """附加信息
#     """

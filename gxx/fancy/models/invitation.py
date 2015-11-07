# -*- coding: utf-8 -*-

import peewee
import config


class Invitation(peewee.Model):
    """邀请码
    """
    code = peewee.CharField(max_length=8)
    sid = peewee.IntegerField(null=True)
    is_valid = peewee.BooleanField(default=True)

    class Meta:
        database = config.database_none
        db_table = "t_invitation"

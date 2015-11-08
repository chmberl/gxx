# -*- coding: utf-8 -*-

from fancy.models import initial


INTALLED_MODELS = initial.INTALLED_MODELS


def create_table(model):
    try:
        model.create_table()
    except:
        pass


def create_tables():
    map(create_table, INTALLED_MODELS)

# -*- coding: utf-8 -*-
import requests
import json

url = "http://sendcloud.sohu.com/webapi/mail.send_template.json"

API_USER = ""
API_KEY = ''

sub_vars = {
    'to': ['bl.com'],
    'sub': {
        '%name%': ['zbl'],
        '%url%': ['www..com'],
    }
}

params = {
    "api_user": API_USER,
    "api_key": API_KEY,
    "template_invoke_name": "test_template_active",
    "substitution_vars": json.dumps(sub_vars),
    "to": "bl.z@foxmail.com",
    "from": "chmberl@gmail.com",
    "fromname": "SendCloud",
    "subject": "SendCloud python common",
    "html": "欢迎使用SendCloud",
    "resp_email_id": "true",
}


r = requests.post(url, data=params)

print r.text
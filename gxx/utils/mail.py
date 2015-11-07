# -*- coding: utf-8 -*-

import json
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape
from tornado import ioloop
import config


def callback(response):
    print response.code


class SendMail(object):

    def __init__(self, url, key, sender, **kwargs):
        AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient'
        )
        self.url = url
        self.key = key
        self.sender = sender
        self.kwargs = kwargs
        self.http_client = AsyncHTTPClient()

    def _parseurl(self, dic):
        ret = []
        for k, v in dic.items():
            ret.append("%s=%s" % (k, url_escape(v, False)))
        return "&".join(ret)

    def callback(self, response):
        pass

    def send(self):
        url = self.url
        params = self.set_params()
        body = self._parseurl(params)
        if "auth_username" in self.kwargs:
            auth_username = self.kwargs.pop("auth_username")
            self.http_client.fetch(url, method="POST", body=body,
                                   callback=self.callback,
                                   auth_username=auth_username,
                                   auth_password=self.key,
                                   follow_redirects=True,
                                   validate_cert=False)
        else:
            self.http_client.fetch(url, method="POST", body=body,
                                   callback=callback, follow_redirects=True,
                                   validate_cert=False)

    def set_params(self):
        raise NotImplementedError("must be implement `set_params` method")


class TemplateSendMail(SendMail):

    def __init__(self, url, key, sender, template, sub_vars, *args, **kwargs):
        self.template = template
        self.sub_vars = sub_vars
        super(TemplateSendMail, self).__init__(url, key, sender, **kwargs)


class SendCloudTemplate(TemplateSendMail):

    def __init__(self, template, sub_vars, sender=None,
                 sender_name=None, *args, **kwargs):
        self.template = template
        self.sub_vars = sub_vars
        sender = sender or config.SENDCLOUD_SENDER
        self.sender_name = sender_name or config.SENDCLOUD_SENDER_NAME
        self.user = config.SENDCLOUD_USER
        url = config.SENDCLOUD_TEMPLALTE_URL
        key = config.SENDCLOUD_KEY
        super(SendCloudTemplate, self).__init__(url, key, sender, template,
                                                sub_vars, **kwargs)

    def set_params(self):
        if "subject" in self.kwargs:
            subject = self.kwargs.get("subject")
        else:
            subject = ""
        params = {
            "api_user": self.user,
            "api_key": self.key,
            "template_invoke_name": self.template,
            "substitution_vars": json.dumps(self.sub_vars),
            "from": self.sender,
            "fromname": self.sender_name,
            "subject": subject,
            "resp_email_id": "true",
        }
        return params


class MailGun(SendMail):

    def __init__(self, to, content, **kwargs):
        self.to = to
        url = config.MAILGUN_URL
        key = config.MAILGUN_KEY
        sender = config.MAILGUN_SENDER
        self.content = content
        super(MailGun, self).__init__(url, key, sender, kwargs)

    def set_params(self):
        if "subject" in self.kwargs:
            subject = self.kwargs.get("subject")
        else:
            subject = ""
        to = self.to
        content = self.content
        params = {
            "from": self.sender,
            "to": to,
            "subject": subject,
            "html": content
        }
        return params


def send_active_mail(user, active_uuid, mail=None):
    if mail == "sendcloud":
        template = config.SENDCLOUD_ACTIVE_TEMPLATE
        mail = config.MAIL_URL % active_uuid
        sub_vars = {
            'to': [user.email],
            'sub': {
                "%name%": [user.username],
                "%url%": [mail]
            }
        }
        subject = "fancy注册激活"
        SendCloudTemplate(template, sub_vars, subject=subject).send()
    else:
        content = config.MAILGUN_ACTIVE_CONTENT
        MailGun(user.email, content).send()


if __name__ == "__main__":
    def main():
        pass
    io_loop = ioloop.IOLoop.instance()
    io_loop.run_sync(main)
    io_loop.start()

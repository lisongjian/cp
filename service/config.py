#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

"""设置页面相关

"""

import tornado.escape
import tornado.web
import urllib

from protocols import WebBaseHandler
from models import feedbacks, options

class ConfigHandler(WebBaseHandler):
    """ 设置页面 """

    @tornado.web.authenticated
    def get(self):
        data = self.current_user
        download_url = urllib.quote(options.get_url())
        self.render("setting/setting.html", data=data, download_url=download_url)


class FAQHandler(WebBaseHandler):
    """ 常见问题 """

    @tornado.web.authenticated
    def get(self):
        self.render("setting/question.html")


class ContactHandler(WebBaseHandler):
    """ 联系我们 """

    @tornado.web.authenticated
    def get(self):
        self.render("setting/contact.html")


class FeedbackHandler(WebBaseHandler):
    """ 意见反馈 """

    @tornado.web.authenticated
    def get(self):
        self.render("setting/feedback.html")

    @tornado.web.authenticated
    def post(self):
        params = {}
        for key in ['type', 'task', 'desc']:
            params[key] = tornado.escape.xhtml_escape(self.get_argument(key, ''))

        params['uid'] = self.current_user['uid']
        feedbacks.new_feedback(**params)
        self.return_success()

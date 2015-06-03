#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author cairuitao@gmail.com
#
""" 服务器封装，处理各服务器初始化、重启等 """

import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.wsgi
import gevent.wsgi
import yaml
import logging
import os
import signal

from tornado.options import define, options
from utils import YamlLoader

define("address", default='127.0.0.1', help="绑定指定地址", type=str)
define("port", default=8888, help="绑定指定端口", type=int)
define("debug", default=False, help="是否开启Debug模式", type=bool)
define("autoreload", default=False, help="代码变化的时候是否自动加载代码", type=bool)
define("config", default="settings.yaml", help="配置文件路径", type=str)


class Application(tornado.wsgi.WSGIApplication):

    def __init__(self, handlers):
        try:
            self.config = yaml.load(file(options.config, 'r'), YamlLoader)
        except yaml.YAMLError as e:
            logging.critical("Error in configuration file: %s", e)

        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'template'),
            login_url="/welcome",
            cookie_secret=self.config['secret']['cookie'],
            session_secret=self.config['secret']['session'],
            debug=options.debug,
        )

        if 'tornado' in self.config:
            settings.update(self.config['tornado'])

        tornado.wsgi.WSGIApplication.__init__(self, handlers, **settings)

        self.startup()

    def startup(self):
        """预先初始化某些工作，数据库链接放这里"""
        pass


def mainloop(app):
    tornado.options.parse_command_line()
    server = gevent.wsgi.WSGIServer((options.address, options.port), app, log=None)

    gevent.signal(signal.SIGTERM, server.close)
    gevent.signal(signal.SIGINT, server.close)
    server.serve_forever()

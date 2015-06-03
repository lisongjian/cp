#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author lisongjian@gmail.com
#

""" JSON交换协议的HTTP Handler """

import tornado.web
import logging
import urlparse
import constants

from tornado.options import options
from crypt import AESCipher
from models import users

try:
    import ujson as json
except ImportError:
    import json


class JSONBaseHandler(tornado.web.RequestHandler):
    """ 用于使用JSON做为数据交换格式的基础Handler """

    def write_json(self, response=None):
        """Write json to client"""
        self.set_header('Content-type', 'application/json; charset=UTF-8')
        self.write(json.dumps(response))
        self.finish()

    def write_error(self, status_code, **kwargs):
        """Function to display custom error page defined in the handler.
        Over written from base handler."""

        reason = None
        err = constants.ERR_PROTOCOL_ERROR
        try:
            reason = kwargs['exc_info'][1].reason
            reason = reason if reason is not None \
                else kwargs['exc_info'][1].log_message
        except AttributeError or TypeError:
            err = constants.ERR_INTERNAL_ERROR

        if options.debug:
            logging.warning("Response err: %s" % reason)
            logging.warning("Request: %s" % self.request)

        self.return_error(err, reason)

    def return_success(self):
        self.write_json({"c": 0})

    def return_result(self, result={}):
        self.write_json({"c": 0, "d": result})

    def return_error(self, code, message=None):
        if not message:
            message = code[1]
        self.write_json({"c": code[0], "d": None, "err": {'msg': message}})

    @property
    def config(self):
        return self.application.config

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def decrypt_params(self, encrypt_param):
        key = self.config['crypt']['aeskey']
        aes = AESCipher(key)
        decrypt_data = aes.decrypt(encrypt_param.replace(' ', '+'))
        return dict([(k, v[0]) for k, v in urlparse.parse_qs(decrypt_data).items()])

    def encrypt_params(self, raw_param):
        key = self.config['crypt']['aeskey']
        aes = AESCipher(key)
        s = []
        for k in raw_param:
            s.append(k + '=' + str(raw_param[k]))
        plain_text = '&'.join(s)
        return aes.encrypt(plain_text)

    def gen_token(self, uid):
        """暂时使用设备指纹作为token todo缓存"""
        user = self.db.get(
            "SELECT * FROM  `user_device` WHERE  `uid` = %s",
            uid)
        return user['fingerprinting']


class Arguments(object):
    """ 过滤后的参数封装 """

    def __init__(self, arguments):
        self.arguments = arguments

    def get(self, key, default=None, strip=True):
        if key in self.arguments:
            v = self.arguments[key]
            if type(v) is list:
                v = v[0]
            if strip:
                v = v.strip()
            return v
        elif default is not None or "" == default:
            return default
        else:
            raise tornado.web.HTTPError(401, reason=("Argument %s is required" % key))


def unpack_arguments(with_phone=True):
    """ 解密s参数 """

    def unpack_arguments_wrap(method):
        def wrapper(self, *args, **kwargs):
            s = None
            if self.request.method == "POST":
                s = self.request.body
            else:
                s = self.get_argument('s', None)
                if s:
                    s = s.encode('utf-8')
            if not s:
                self.arguments = Arguments(self.request.arguments)
            else:
                try:
                    self.arguments = Arguments(self.decrypt_params(s))
                except:
                    return self.return_error(constants.ERR_DECRYPT_FAIL)

            if self.arguments.get('phone', ""):
                user_info = users.get_info_byphone(self.arguments.get('phone'))
                if not user_info:
                    pass
                else:
                    self.current_user = users.get_info_byphone(self.arguments.get('phone'))
                #print self.arguments.get('phone', "")
            #else:
             #   if with_phone:
              #      pass
                    #return self.return_error(constants.ERR_INVALID_SCOPEID)

            return method(self, *args, **kwargs)
        return wrapper
    return unpack_arguments_wrap

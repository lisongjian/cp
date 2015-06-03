#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

import yaml
import os.path
import hashlib
import logging
import base64
import constants

from models import users
from user_agents import parse
from hashlib import sha256
from hmac import HMAC

class YamlLoader(yaml.Loader):
    """ Yaml loader

    Add some extra command to yaml.

    !include:
        see http://stackoverflow.com/questions/528281/how-can-i-include-an-yaml-file-inside-another
        include another yaml file into current yaml
    """

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(YamlLoader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, YamlLoader)

YamlLoader.add_constructor('!include', YamlLoader.include)

class Loggers(object):
    """简单的logging wrapper"""

    def __init__(self):
        self.loggers = {}

    def use(self, log_name, log_path):
        if not log_name in self.loggers:
            logger = logging.getLogger(log_name)
            logger.setLevel(logging.INFO)
            if not logger.handlers:
                fh = logging.FileHandler(log_path)
                fh.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(message)s')
                fh.setFormatter(formatter)
                logger.addHandler(fh)
            self.loggers[log_name] = logger
        return self.loggers[log_name]

loggers = Loggers()

class Base34():
    """ base62编码器 """
    """ 邀请码密码加解密 """

    def __init__(self):
        self.alphabet = "9AXCZ3U5D1F2HIJKM6NE7PQ4RSTV8GWBLY"
        self.base = len(self.alphabet)

    def decode(self, string):
        string = str(string)
        strlen = len(string)
        num = 0
        idx = 0
        for char in string:
            power = (strlen - (idx + 1))
            num += self.alphabet.index(char) * (self.base ** power)
            idx += 1
        return num

    def encode(self, num):
        num = int(num)
        if num == 0:
            return self.alphabet[0]
        arr = []
        while num:
            rem = num % self.base
            num = num // self.base
            arr.append(self.alphabet[rem])
        arr.reverse()
        return ''.join(arr)

base34 = Base34()

def get_platform(user_agent):
    """ 获取客户端系统类型, 1:Android, 2:IOS """
    ua = parse(user_agent)
    os_family = ua.os.family
    if os_family == 'iOS':
        platform = constants.PLATFORM_IOS
    elif os_family == 'Android':
        platform = constants.PLATFORM_ANDROID
    else:
        platform = constants.PLATFORM_UNKNOWN
    return platform


def md5(raw_str):
    return hashlib.new("md5", str(raw_str)).hexdigest()


def sha1(raw_str):
    return hashlib.new("sha1", str(raw_str)).hexdigest()


def gen_token(phone, pwd):
    raw_str = '%s%s' % (phone, pwd)
    return sha1(md5(raw_str))

def valid_pwd(uid, pwd):
    info = users.get_info(uid)
    if md5(base34.encode(pwd)) == info['pwd']:
        return True
    else:
        return False

def md5_sign(params={}):
    """ 兑吧签名验证 """
    # 排序
    def ksort(d):
        return [(k, d[k]) for k in sorted(d.keys())]

    sorted_params = ksort(params)
    raw_str = ''
    for p in sorted_params:
       raw_str += str(p[1])
    sign = hashlib.new("md5", raw_str).hexdigest()

    return sign

def encrypt_pwd(pwd, salt=None):
    """ 密码加密 """
    if salt is None:
        salt = os.urandom(8)
    else:
        salt = base64.b64decode(salt)

    result = pwd
    for i in xrange(3):
        result = HMAC(str(result), salt, sha256).hexdigest()

    return base64.b64encode(salt), result


def validate_pwd(enc_pwd, in_pwd, salt):
    """ 验证密码 """
    return enc_pwd == encrypt_pwd(in_pwd, salt)[1]


def push(phone, msg):
    import jpush as jpush
    from conf import app_key, master_secret
    _jpush = jpush.JPush(app_key, master_secret)

    push = _jpush.create_push()
    push.audience = jpush.audience(
                jpush.alias(phone)
            )
    push.notification = jpush.notification(alert=msg)
    push.platform = jpush.all_
    push.message = {"msg_content":'test'}
    push.send()


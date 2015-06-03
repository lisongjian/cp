#!/usb/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author lisongjian@youmi.net
#

import random
import base64
import requests
import ujson as json
import constants
import utils
import db
import yaml
import os.path

from datetime import datetime

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

def check_sms(phone, code):
    """ 验证短信验证码 """
    key_name = "suoping:code:%s" % phone
    data = db.redis.get(key_name)
    if not data:
        msg = constants.ERR_CAPTCHA_INVALID
    elif int(code) != int(data):
        msg = constants.ERR_CAPTCHA_ERROR
    else:
        msg = None
        db.redis.delete(key_name)
    return msg


def check_freq_phone(phone):
    """ 检验请求发送频率 """
    key_name = "suoping:wait:%s" % phone
    if db.redis.get(key_name):
        return False
    return True


def check_freq_ip(ip):
    """ 检验单个IP发送数量 """
    pass



def send_sms_ytx(phone, ytx):
    """ 容联云通讯短信验证码 """
    # FIXME 修改为异步 or 消息队列
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    sig = utils.md5(ytx['acid'] + ytx['actoken'] + ts).upper()
    url = '%s/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s' % \
        (ytx['url'], ytx['acid'], sig)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": base64.b64encode(ytx['acid'] + ':' + ts),
    }
    code = str(random.randint(100000, 999999))
    payload = {
        "to": phone,
        "appId": ytx['appid'],
        "templateId": "18791",
        "datas": [code, '10'],
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    result = r.json()
    if result['statusCode'] == '000000':
        return True, code
    elif result['statusCode'] == '112314':
        return False, result['statusCode']
    else:
        return False, result['statusMsg'].encode('utf-8')


def send_sms_tui3(phone, tui3):
    """ 推立方短信验证码 """
    code = random.randint(10000, 99999)
    apikey = tui3['apikey']
    url = "http://tui3.com/api/code/?k=%s&t=%s&c=%s&ti=1" \
        % (apikey, phone, code)
    req = requests.get(url)
    result = req.json()
    if result['err_code'] == 0:
        return True, code
    else:
        return False, None


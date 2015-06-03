#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

import os.path

""" Tornado Server 定义 """
# 接收到关闭信号后多少秒后才真正重启
MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1
# Listen IPV4 only
IPV4_ONLY = True

""" 全局配置常量 """
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

PLATFORM_UNKNOWN = 0
PLATFORM_ANDROID = 1
PLATFORM_IOS = 2

SETTINGS_FILE = "settings.yaml"

""" 协议相关 """
ERR_PROTOCOL_ERROR = (-1001, "协议解析错误")
ERR_INTERNAL_ERROR = (-1002, "内部错误")
# 此处为解密出错，为手机显示故说服务器繁忙
ERR_DECRYPT_FAIL = (-1003, "服务器繁忙，请退出再试！")
ERR_PARAMS_NULL = (-1004, "参数不能为空")

""" 验证相关 """
ERR_CAPTCHA_INVALID = (-2001, "验证码无效")
ERR_CAPTCHA_ERROR = (-2002, "验证码有误，请重新输入！")
ERR_CAPTCHA_FREQUENCY = (-2003, "验证码发送过于频繁，请稍后再试！")
ERR_CAPTCHA_FAIL = (-2004, "验证码发送失败，请重发验证码！")
ERR_CAPTCHA_MANY = (-2005, "该手机号验证码发送超过当日上限！")

""" 手机号码相关 """
ERR_INVALID_PHONE = (-3001, "请填写正确的手机号码")
ERR_HAD_PHONE = (-3002, "该手机号码已注册！请您直接登录")
ERR_HAD_IMEI = (-3003, "一个设备只能绑定一个手机号码")
ERR_IMEI_INVALID = (-3004, "手机序列号不符合规范")

""" 邀请相关 """
ERR_IVCODE_INVALID = (-4001, "请填写合法的邀请码")

""" 用户相关 """
ERR_NO_LOGIN = (-5001, "用户未登录")
ERR_BIND_FAIL = (-5002, "绑定用户失败")
ERR_MD5IFA_FAIL = (-5003, "MD5IFA重复")
ERR_NO_PHONE = (-5004, "抱歉，账号不存在！")
ERR_IN_PWD = (-5005, "您输入的账号或密码有误，请重新输入！")
ERR_IN_TOKEN = (-5006, "")
ERR_IN_VERSION = (-5007, "该版本已经不再支持，请更新新版！")
ERR_IN_TIME = (-5008, "本月不能再次绑定新手机")
ERR_IN_CHANGE = (-5009, "尝试重新绑定设备")

""" 兑换相关 """
ERR_KEY_NOT_MATCH = (-6001, 'AppKey不匹配')
ERR_TIME_NOT_NULL = (-6002, '时间戳不能为空')
ERR_INVALID_TIME = (-6003, '时间戳无效')
ERR_INVALID_SIGN = (-6004, '签名验证失败')

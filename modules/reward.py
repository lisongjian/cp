#!/usb/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author chenjiehua@youmi.net
#
from datetime import date
from models import users, orders, options
import db

def task_prorate(user_info, points):
    if user_info['parent']:
        parent = users.get_info(user_info['parent'])
        if parent['platform'] == user_info['platform'] and user_info['platform'] != 0:
            if parent['vip'] == 1:
                iv_prorate = options.get('vip')
            else:
                iv_prorate = options.get('iv_parent')
            iv_prize = points * int(iv_prorate) / 100
        if iv_prize<1:
            iv_prize=1
        note = u"您的徒弟 %s 完成任务，你分成 %s%%" % \
            (user_info['tid'], iv_prorate)
        oid = orders.new_global_order(
            parent['uid'], parent['points'], iv_prize,
            orders.OTYPE_INVITE, note)
        users.add_iv_points(parent['uid'], iv_prize)
    if user_info['grandfather']:
        grandfather = users.get_info(user_info['grandfather'])
        if grandfather['platform'] == user_info['platform'] and user_info['platform'] != 0:
            iv_prorate = options.get('iv_grandfather')
            iv_prize = points * int(iv_prorate) / 100
        if iv_prize<1:
            iv_prize=1
        note = u"您的徒孙 %s 完成任务，你分成 %s%%" % \
            (user_info['tid'], iv_prorate)
        oid = orders.new_global_order(
            grandfather['uid'], grandfather['points'],
            iv_prize, orders.OTYPE_INVITE, note)
        users.add_iv_points(grandfather['uid'], iv_prize)

def today_earn(uid, points):
    """ 缓存记录今日赚取 """
    key_name = "suoping:earn:%s:%s" % (uid, date.today().strftime("%Y%m%d"))
    rate = int(options.get('rate'))
    data = db.redis.get(key_name)
    if not data:
        db.redis.setex(key_name, "%.2f" %(float(points)/int(rate)), 86400)
    else:
        db.redis.setex(key_name, "%.2f" %((float(data)+(float(points)/int(rate)))), 86400)

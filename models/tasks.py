#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: lisongjian@youmi.net
#

"""用户相关操作

"""

import db
import datetime
""" 锁屏图片url表 """
def get_pic_urls():
    return db.mysql.query("SELECT * FROM `ScreenPic`")

def get_task():
    return db.mysql.query("SELECT * FROM `task`")

def get_task_byid(id):
    data = db.mysql.get("SELECT * FROM `task` WHERE `id`=%s", id)
    return data['earn'] if data else 0

def user_task(uid):
    return db.mysql.query("SELECT * FROM `user_task` WHERE `uid` = %s",uid)

def get_task_info(uid, task_id):
    return db.mysql.get("SELECT * FROM `user_task` WHERE `uid` = %s \
                       AND `task_id` = %s LIMIT 1", uid, task_id)

def new_task(uid, task_id):
    return db.mysql.execute(
        "INSERT INTO `user_task`(`uid`,`task_id`,`create_time`)"
        "VALUES(%s, %s, %s)", uid, task_id, datetime.datetime.now())

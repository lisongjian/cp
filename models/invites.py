#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

"""邀请相关操作

"""

import db

from datetime import date

@db.db_cache("invite", 2)
def get_invite(uid, day):
    return db.mysql.get(
        "SELECT * FROM `invite_counts` WHERE `uid` = %s "
        "AND `date` = %s LIMIT 1", uid, day)

def new_invite(uid, son=0, grandson=0):
    day=date.today().strftime("%Y%m%d")
    return db.mysql.execute(
        "INSERT INTO `invite_counts`(`uid`, `sons`, `grandsons`, `date`)"
        "VALUES(%s, %s, %s, %s)", uid, son, grandson, day)

def add_invite(uid, son=0, grandson=0):
    day=date.today().strftime("%Y%m%d")
    db.del_cache("invite", uid, day)
    return db.mysql.execute(
        "UPDATE `invite_counts` SET `sons` = `sons` + %s, "
        "`grandsons` = `grandsons` + %s WHERE `uid` = %s "
        "AND `date` = %s", son, grandson, uid, day)


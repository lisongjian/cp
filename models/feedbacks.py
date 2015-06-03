#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

"""用户反馈操作

"""

import db

def new_feedback(uid, type, task, desc, platform):
    return db.mysql.execute(
        "INSERT INTO `feedbacks`(`uid`, `type`, `task`, `desc`, `platform`)"
        "VALUES(%s, %s, %s, %s, %s)", uid, type, task, desc, platform)

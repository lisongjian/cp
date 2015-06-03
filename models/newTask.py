#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenyongjian@youmi.net
#

import db

"""新手任务表操作"""

def get(uid):
    return db.mysql.get(
        "SELECT * FROM `new_task` WHERE uid = %s",uid
    )

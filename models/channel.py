#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenyongjian@youmi.net
#

import db

"""渠道操作"""

def get_id(username):
    return db.mysql.get(
        "SELECT `id` FROM `channel` WHERE `username` = %s", username
    )

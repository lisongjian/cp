#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenyongjian@youmi.net
#

"""版本信息操作

"""

import db
""" version表 """
def get():
    return db.mysql.query("SELECT * FROM `version`")

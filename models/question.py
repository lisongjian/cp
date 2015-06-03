#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenyongjian@youmi.net
#

"""F & Q操作

"""

import db
""" question表 """
def get():
    return db.mysql.query("SELECT * FROM `question`")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: lisongjian@youmi.net
#

import db

def get_ifa(idfa):
    data = db.mysql.get(
        "SELECT * FROM `wallad_clicks` WHERE `status` = 0 AND \
        `create_time`>=(Curdate()-7) AND `idfa`=%s LIMIT 1", idfa)
    return data if data else None

def set_user_pkg(uid, pkg):
    return db.mysql.execute(
        "UPDATE `users` SET `pkg` = %s WHERE `uid`= %s", pkg, uid)


def get_callback_byimei(imei):
    return db.mysql.get(
        "SELECT * FROM `wallad_clicks` WHERE `idfa` = %s and appType=1 LIMIT 1", imei)

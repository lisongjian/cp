#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: lisongjian@youmi.net
#

import db

@db.db_cache('option')
def get(key):
    data = db.mysql.get(
        "SELECT `values` FROM `options` WHERE `key` = %s", key)
    return data['values'] if data else 0

def get_url():
    data = db.mysql.get(
        "SELECT `download_url` FROM `changelogs` ORDER BY `id` DESC")
    return data['download_url'] if data else ''

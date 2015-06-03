#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenyongjian@youmi.net
#

import db

"""IMEI操作"""

def set_imei(uid, phone, imei):
    return db.mysql.execute(
        "INSERT INTO `imei` VALUES(null,%s,%s,%s)", uid, phone, imei
    )

"""IMEI限制"""    
def get_imei_limit(phone):
	return db.mysql.get("SELECT COUNT(*) AS total FROM `imei_limit` WHERE `phone` = %s", phone)

def set_imei_limit(phone, imei):
	return db.mysql.execute(
		"INSERT INTO `imei_limit` VALUES(null, %s, %s, 1)", phone, imei
	)
	
def get_imei_byphone(phone):
	return db.mysql.get("SELECT * FROM `imei_limit` WHERE `phone` = %s LIMIT 1", phone)
    
def update_status_limit(phone, imei):
	return db.mysql.execute(
		"UPDATE `imei_limit` SET `imei` = %s, `status`=`status`+1 WHERE `phone` = %s", imei, phone
	)

"""限制日期"""
def get_limit_time():
	return db.mysql.get(
		"SELECT * FROM `date_limit` LIMIT 1"
	)
	
def update_limit_time(timing):
	return db.mysql.execute(
		"UPDATE `date_limit` SET `limit_date` = %s", timing
	)
	
def update_imei_limit():
	return db.mysql.execute(
		"UPDATE `imei_limit` SET `status` = 1"
	)

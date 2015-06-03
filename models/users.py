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
import time

""" users表 """
def new_user(ip, ip_address, phone, pwd, imei, pkg):
    number = int(time.time()) - 1422000000
    user=db.mysql.execute(
        "INSERT INTO `users`(`ip`, `ip_address`, `phone`, `platform`, `pwd`, `imei`, `pkg`)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s)", ip, ip_address, phone, 1, pwd, imei, pkg)
    db.mysql.execute(
        "UPDATE `users` SET `tid` = %s WHERE `uid` = %s", \
        int(number)+int(user), user)
    return user

#IMEI
def check_imei(imei):
    return db.mysql.get(
        "SELECT `imei` FROM `users` WHERE `imei` = %s", imei
    )

def update_pwd(uid, new_pwd):
    return db.mysql.execute(
        "UPDATE `users` SET `pwd` = %s WHERE `uid` = %s", new_pwd, uid)

def get_info(uid):
    return db.mysql.get(
        "SELECT * FROM `users` WHERE `uid` = %s", uid)

def get_info_byphone(phone):
    return db.mysql.get(
        "SELECT * FROM `users` WHERE `phone` = %s and `platform`=1", phone)

def get_info_bytid(tid):
    return db.mysql.get(
        "SELECT * FROM `users` WHERE `tid` = %s", tid)

def set_user_bonus(uid):
    return db.mysql.execute(
        "UPDATE `users` SET `gift` = 0  WHERE `uid` = %s", uid)

@db.db_cache('user_total', count=0, ttl=300)
def count_users():
    data = db.mysql.get(
        "SELECT count(`uid`) AS dcount, sum(`sons`) AS dsum FROM `users`")
    return data

def add_tt_points(uid, points):
    return db.mysql.execute(
        "UPDATE `users` SET `points` = `points` + %s, "
        "`tt_points` = `tt_points` + %s WHERE `uid` = %s",
        points, points, uid)

def add_iv_points(uid, points):
    return db.mysql.execute(
        "UPDATE `users` SET `points` = `points` + %s, "
        "`iv_points` = `iv_points` + %s, `tt_points` = `tt_points` + %s "
        "WHERE `uid` = %s", points, points, points, uid)

def sub_ex_points(uid, points):
    return db.mysql.execute(
        "UPDATE `users` SET `points` = `points` - %s, "
        "`ex_points` = `ex_points` + %s WHERE `uid` = %s",
        points, points, uid)

def add_ex_points(uid, points):
    return db.mysql.execute(
        "UPDATE `users` SET `points` = `points` + %s, "
        "`ex_points` = `ex_points` - %s WHERE `uid` = %s",
        points, points, uid)

def set_invite(uid, parent, grandfather):
    return db.mysql.execute(
        "UPDATE `users` SET `parent` = %s, `grandfather` = %s "
        "WHERE `uid` = %s", parent, grandfather, uid)

def add_invite(uid, son=0, grandson=0):
    return db.mysql.execute(
        "UPDATE `users` SET `sons` = `sons` + %s, "
        "`grandsons` = `grandsons` + %s WHERE `uid` = %s ",
        son, grandson, uid)

def update_info(uid, username, sex, place):
    return db.mysql.execute(
        "UPDATE `users` SET `username` = %s, `sex` = %s, `place` = %s "
        "WHERE `uid` = %s", username, sex, place, uid)

def update_avatar(uid, avatar):
    return db.mysql.execute(
        "UPDATE `users` SET `headimg` = %s WHERE `uid` = %s",
        avatar, uid)

def set_platform(uid, platform):
    return db.mysql.execute(
        "UPDATE `users` SET `platform` = %s WHERE `uid` = %s",
        platform, uid)

def set_phone(uid, phone):
    return db.mysql.execute(
        "UPDATE `users` SET `phone` = %s WHERE `uid` = %s",
        phone, uid)

def set_last_login(uid, time):
    return db.mysql.execute(
        "UPDATE `users` SET `last_login` = %s WHERE `uid` = %s",
        time, uid)


""" devices表 """
def new_device(oid, uid, cid, mac, ifa, aicid, udid, attr, tid):
    return db.mysql.execute(
        "INSERT INTO `devices`(`oid`, `uid`, `cid`, `mac`, `ifa`, "
        "`aicid`, `udid`, `attr`, `tid`)VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        oid, uid, cid, mac, ifa, aicid, udid, attr, tid)

@db.db_cache("device")
def get_device(oid):
    return db.mysql.get(
        "SELECT * FROM `devices` WHERE `oid` = %s LIMIT 1", oid)

@db.db_cache("device_ifa")
def get_device_byifa(ifa):
    return db.mysql.get(
        "SELECT * FROM `devices` WHERE `ifa` = %s LIMIT 1", ifa)

@db.db_cache("device_mac")
def get_device_bymac(mac):
    return db.mysql.get(
        "SELECT * FROM `devices` WHERE `mac` = %s LIMIT 1", mac)

def update_oid(ifa, noid, ooid):
    return db.mysql.execute(
        "UPDATE `devices` SET `same_oid`=%s, `oid` = %s, \
        `old_oid` = %s WHERE `ifa` = %s",
        1,noid, ooid, ifa)

def update_dname(ifa, name):
    return db.mysql.execute(
        "UPDATE `devices` SET `device_name`=%s WHERE `ifa` = %s" ,name, ifa)

def get_user_ip(uid, ip):
    return db.mysql.get(
        "SELECT * FROM `ip_info` WHERE `uid` = %s  AND `ip` = %s LIMIT 1", uid, ip)

def set_user_ip(ip, uid, ip_address):
    ip_info=db.mysql.execute(
        "INSERT INTO `ip_info`(`ip`, `uid`, `ip_address`)"
        "VALUES(%s, %s, %s)", ip, uid, ip_address)
    return ip_info




#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: lisongjian@youmi.net
#

"""任务信息相关

"""
import protocols
import utils
import constants
import random
import time
from models import tasks, options, users, orders
from datetime import date


class GetpicHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        params = {}
        for key in ['sw', 'sh', 'phone']:
            params[key] = self.arguments.get(key, "")
        all_url = tasks.get_pic_urls()
        urls = []
        for url in all_url:
            urls.append(url['url'])
        self.return_result({"list": urls})


class GetadHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        pass

class GetUnlockHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        # TODO 后台设置概率， 赚取, 更新token算法
        i = 1
        tokens = []
        for i in range(1):
            tokens.append({
                "token": 1,
                "earn": 0.02,
            })
        count = orders.count_unlock_orders(self.current_user['uid'])
        if int(count['dcount'])<=50:
            times = self.redis.get("suoping:deny:"+str(self.current_user['uid']))
            if not times:
                self.return_result({"ts": tokens})
            else:
                token = []
                self.return_result({"ts": token})
        else:
            token =[]
            self.return_result({"ts": token})

class UnlockHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        params = {}
        for key in ['token', 'phone']:
            params[key] = self.arguments.get(key, "")
        #i = random.randint(1,5)
        count = orders.count_unlock_orders(self.current_user['uid'])
        #判断总次数
        if int(count['dcount'])>50:
            self.return_result({"st":-1,"title":"1"})
        else:
            #判断 20 分钟之内 解锁
            times = self.redis.get("suoping:deny:"+str(self.current_user['uid']))
            if times:
                self.return_result({"st":-1,"title":"1"})
            else:
                i = 1
            #if params['token'] == utils.md5(i):
                if i == int(params['token']):
                    #条件通过，设置缓存20分钟
                    self.redis.setex("suoping:deny:"+str(self.current_user['uid']),time.time(),1200)
                    self._today_earn(self.current_user['uid'], 2)
                    oid = orders.new_global_order(
                        self.current_user['uid'], self.current_user['points'], 2,
                        5, 'Good luck!你完成解锁获得奖励')
                    users.add_tt_points(self.current_user['uid'], 2)
                    task = tasks.get_task_info(self.current_user['uid'], 6)
                    if not task:
                        earn = tasks.get_task_byid(6)
                        tasks.new_task(self.current_user['uid'], 6)
                        orders.new_global_order(
                            self.current_user['uid'], self.current_user['points'], earn,
                            1, '恭喜您完成新手任务-首次右滑解锁,获得奖励')
                        users.add_tt_points(self.current_user['uid'], earn)
                        self._today_earn(self.current_user['uid'], earn)
                    self.return_result({"st":0,})
                else:
                    self.return_result({"st":-1,"title":"1"})
            #self.return_error(constants.ERR_IN_TOKEN)

    def _today_earn(self, uid, points):
        """ 缓存记录今日赚取 """
        key_name = "suoping:earn:%s:%s" % (uid, date.today().strftime("%Y%m%d"))
        rate = options.get('rate')
        data = self.redis.get(key_name)
        if not data:
            self.redis.setex(key_name, "%.2f" %(float(points)/int(rate)), 86400)
        else:
            self.redis.setex(key_name, "%.2f" %((float(data)+(float(points)/int(rate)))), 86400)




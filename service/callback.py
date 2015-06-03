#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: lisongjian@youmi.net
#

"""广告任务回调

"""

import utils
import sys
import ujson as json
import jpush
from datetime import date
from modules import reward
from models import users, orders, options, tasks
from protocols import JSONBaseHandler

reload(sys)
sys.setdefaultencoding('utf-8')


class CallbackHandler(JSONBaseHandler):
    """ 广告回调响应 """
    def get(self, platform):
        # 日志打印
        log_path = self.config['log']['callback']
        utils.loggers.use('callback', log_path).info(self.request.uri)
        params = {}
        if platform == 'youmiaos':
            self.write('ok')
            self._platform = 1
            params['sign'] = self.get_argument('sig','')
            sign = self.check_sign_aos()
        elif platform == 'youmiios':
            self._platform = 2
            params['sign'] = self.get_argument('sign','')
            sign = self.check_sign_ios()
        else:
            return self.write('what the fuck?')

        keys = ['order', 'ad', 'adid', 'user', 'points', \
                'price', 'time', 'device', 'trade_type']
        for key in keys:
            params[key] = self.get_argument(key, '')
        if not params:
            return self.write('arguments is required')
        self.write('ok')

        # 参数校验，测试完成后取消注释 FIXME
        if sign != params['sign']:
            return self.write('invalid sign')

        self.save_order(**params)

    def save_order(self, order, ad, adid, user, points,
                   price, time, device, sign, trade_type):
        """保存订单"""
        user_info = users.get_info_byphone(user)
        if not user_info:
            user_info = users.get_info(user)
            if not user_info:
                return self.write('not user')
        # 小助手不加积分
        if int(adid) == 7658:
            return self.write('qiankaxiaozhushou')
        rate = options.get('rate')
        # 用户被邀请
        if user_info['parent']:
            parent = users.get_info(int(user_info['parent']))
            if parent['platform'] == user_info['platform'] and user_info['platform'] != 0:
                reward.task_prorate(user_info, int(points))
                # 师傅收益缓存今日赚取
                if parent['vip'] == 1:
                    iv_prorate = options.get('vip')
                else:
                    iv_prorate = options.get('iv_parent')
                self._today_earn(user_info['parent'],"%.2f" %(int(points) * int(iv_prorate)/100))
        if user_info['grandfather']:
            grandfather = users.get_info(int(user_info['grandfather']))
            if grandfather['platform'] == user_info['platform'] and user_info['platform'] != 0:
                iv_gprorate = options.get('iv_grandfather')
                self._today_earn(user_info['grandfather'], "%.2f" %(int(points) * int(iv_gprorate)/100))
        if user_info['parent'] or user_info['grandfather']:
            count_otype = int(orders.count_callback_orders(user_info['uid'])['dcount'])
            if count_otype == 0:
                parent = users.get_info(user_info['parent'])
                if parent['platform'] == user_info['platform'] and user_info['platform'] != 0:
                    self._today_earn(user_info['parent'], 2*int(rate))
                    note = u'您的徒弟完成任务，奖励师傅2元'
                    oid = orders.new_global_order(user_info['parent'], parent['points'], 2*int(rate), orders.OTYPE_INVITE, note)
                    users.add_iv_points(parent['uid'], 2*int(rate))
        order_info = orders.get_callback_order(order)
        if not order_info:
            if int(trade_type) == 1 or trade_type == '':
                note = u"恭喜您成功下载安装 %s ,获得奖励" % ad
                # 试玩奖励
                task = tasks.get_task_info(user_info['uid'], 1)
                if not task:
                    earn = tasks.get_task_byid(1)
                    orders.new_global_order(user_info['uid'], user_info['points'], earn,
                    1, '恭喜您完成新手任务-首次试玩 ,获得奖励')
                    tasks.new_task(user_info['uid'], 1)
                    users.add_tt_points(user_info['uid'], earn)
                    self._today_earn(user_info['uid'], earn)
            elif int(trade_type) == 2:
                note = u"恭喜您完成追加任务 %s ,获得奖励" % ad
                task = tasks.get_task_info(user_info['uid'], 4)
                if not task:
                    earn = tasks.get_task_byid(4)
                    orders.new_global_order(user_info['uid'], user_info['points'], earn,
                    1, '恭喜您完成新手任务-首次深度任务 ,获得奖励')
                    tasks.new_task(user_info['uid'], 4)
                    users.add_tt_points(user_info['uid'], earn)
                    self._today_earn(user_info['uid'], earn)

            oid = orders.new_global_order(
                user_info['uid'], user_info['points'], points,
                orders.OTYPE_TASK, note)
            users.add_tt_points(user_info['uid'], points)
            price = "%.2f" % (float(points)/int(rate))
            msg = note +  str(price) +u'元'
            params = {
                "order": order,
                "oid": oid,
                "ad": ad,
                "adid": adid,
                "uid": user_info['uid'],
                "points": points,
                "price": price,
                "device": device,
                "sig": sign,
                "platform": self._platform,
                "trade_type": trade_type,
                "pkg" : user_info['pkg']
            }
            orders.new_callback_order(**params)
            self._today_earn(user_info['uid'], points)
            self._callback_record(user_info['uid'], ad, adid, points)
            utils.push(user_info['phone'],msg.encode('utf-8'))

    def check_sign_ios(self):
        """ ios验证签名 """
        args = self.request.arguments
        kv = []
        for key in args:
            if key != 'sign':
                value = args[key][0].decode('utf-8')
                kv.append('%s=%s' % (key, value))
        raw_str = ''
        for s in sorted(kv):
            raw_str += s
        raw_str += self.config['ymserver_key']['ios']
        return utils.md5(raw_str)

    def check_sign_aos(self):
        """ aos验证签名 """
        raw_param = [self.config['ymserver_key']['aos']]
        keys = ['order', 'app', 'user', 'chn', 'ad', 'points']
        for key in keys:
            value = self.get_argument(key, '')
            raw_param.append(value)
        raw_str = '||'.join(raw_param)
        return utils.md5(raw_str)[12:20]

    def _today_earn(self, uid, points):
        """ 缓存记录今日赚取 """
        key_name = "suoping:earn:%s:%s" % (uid, date.today().strftime("%Y%m%d"))
        rate = options.get('rate')
        data = self.redis.get(key_name)
        if not data:
            self.redis.setex(key_name, "%.2f" %(float(points)/int(rate)), 86400)
        else:
            self.redis.setex(key_name, "%.2f" %((float(data)+(float(points)/int(rate)))), 86400)

    def _callback_record(self, uid, ad, adid, points):
        rate = options.get('rate')
        """ 缓存回调记录，用于客户端轮询 """
        rec = {
            "ad": ad,
            "watid": adid,
            "points": "%.2f" %(float(points)/int(rate)),
            "aname": self.config['app']['name'],
        }
        key_name = "suoping:callback:%s" % uid
        data = self.redis.get(key_name)
        if not data:
            result = []
            result.append(rec)
        else:
            result = json.loads(data)
            result.append(rec)
        self.redis.setex(key_name, json.dumps(result), 86400*7)



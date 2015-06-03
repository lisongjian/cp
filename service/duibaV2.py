#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

"""兑吧兑换接口

"""
import tornado.web
import time
import constants
import utils
import IP
import urllib
import protocols
from models import users, orders, options

class DuibaBaseHandler(protocols.JSONBaseHandler):
    """ 兑吧基础类 """

    @property
    def appKey(self):
        return self.config['duiba']['appKey']

    @property
    def appSecret(self):
        return self.config['duiba']['appSecret']

    def get_params(self):
        params = {}
        kv = self.request.arguments
        for k in kv:
            params[k] = kv[k][0].decode('utf-8')
        return params

    def get_sign(self, params={}):
        """ 兑吧md5签名 """
        params = self._ksort(params)
        raw_str = ''
        for p in params:
            raw_str += str(p[1])
        return utils.md5(raw_str)

    def _ksort(self, d={}):
        """ 参数排序 """
        return [(k, d[k]) for k in sorted(d.keys())]

    def check_sign(self, params={}):
        """ 验证签名 """
        if params['appKey'] != self.appKey:
            return False, constants.ERR_KEY_NOT_MATCH
        elif params['timestamp'] == '':
            return False, constants.ERR_TIME_NOT_NULL
        params['appSecret'] = self.appSecret
        sign = params.pop('sign')
        if sign != self.get_sign(params):
            return False, constants.ERR_INVALID_SIGN
        return True, ''


class LoginHandler(DuibaBaseHandler):
    """ 兑吧免登陆url """
    @protocols.unpack_arguments()
    def get(self):
        timestamp = int(time.time() * 1000)
        uid = self.current_user['uid']
        rate = options.get('rate')
        points = int (self.current_user['points']/float(rate))
        #points = self.current_user['points']
        params = {
            'uid': uid,
            'credits': points,
            'appSecret': self.appSecret,
            'appKey': self.appKey,
            'timestamp': timestamp
        }
        sign = self.get_sign(params)
        url = "http://www.duiba.com.cn/autoLogin/autologin?uid=%s&credits=%s&appKey=%s&sign=%s&timestamp=%s" \
                % (uid, points, self.appKey, sign, timestamp)
        log_path = self.config['log']['duiba']
        utils.loggers.use('duiba', log_path).info(url)
        self.return_result({"url": url})
        # url = urllib.quote(url)
        # self.render("exchange/exchange.html", url=url)


class ConsumeHandler(DuibaBaseHandler):
    """ 积分消耗 """
    @protocols.unpack_arguments(with_phone=False)
    def get(self):
        rate = options.get('rate')
        log_path = self.config['log']['duiba']
        utils.loggers.use('duiba', log_path).info(self.request.uri)
        params = self.get_params()
        # 兑换地址
        #address = ''
        #for add in ['alipay', 'phone', 'qq']:
        #    address = params[add] if params[add] else address

        succ, msg = self.check_sign(params)
        if not succ:
            result = {"status": "fail", "message": "参数校验失败", "errorMessage": msg[1]}
            return self.write_json(result)

        user_info = users.get_info(params['uid'])
        if not user_info:
            result = {"status": "fail", "message": "兑换失败", "errorMessage": "用户不存在"}
            return self.write_json(result)

        succ, msg = self._check_user(user_info, params['credits'])
        if not succ:
            result = {"status": "fail", "message": "兑换失败", "errorMessage": msg[1]}
            return self.write_json(result)

        # 全局订单 FIXME 采用事务
        oid = orders.new_global_order(
            user_info['uid'], user_info['points'], -int(params['credits'])*int(rate),
            orders.OTYPE_EXCHANGE, params['description'])

        ip_address = IP.find(params['ip']) if params['ip'] else None
        params['facePrice'] = int(params['facePrice']) / 100.0
        params['actualPrice'] = int(params['actualPrice']) / 100.0
        exchange_params = {
            'uid': user_info['uid'],
            'oid': oid,
            'points': int(params['credits'])*int(rate),
            'face_price': params['facePrice'],
            'actual_price': params['actualPrice'],
            'description': params['description'],
            #'address': address,
            'address': params['params'],
            'order_num': params['orderNum'],
            'extype': params['type'],
            'ip': params['ip'],
            'ip_address': ip_address,
            'status': 10,
            'wait_audit': 1 if params['waitAudit'].lower() == 'true' else 0,
            'pkg' : user_info['pkg']
        }
        orders.new_exchange_order(**exchange_params)
        users.sub_ex_points(user_info['uid'], int(params['credits'])*int(rate))
        result = {
            "status": "ok",
            "message": "兑换成功",
            "errorMessage": "",
            "data": {
                "bizId": oid,
                "credits": int((user_info['points'] - int(params['credits'])*int(rate))/int(rate)),
            },
        }
        self.write_json(result)

    def _check_user(self, user_info, credits):
        """ 检查用户 """
        succ, msg = True, None
        if user_info['status'] in [-1, -2]:
            succ, msg = False, constants.ERR_INVALID_USER
        if user_info['points'] < int(credits):
            succ, msg = False, constants.ERR_NOT_ENOUGH_POINTS
        return succ, msg

    def _check_address(self, user_info, address):
        """ 检查兑换地址 """
        pass


class NotifyHandler(DuibaBaseHandler):
    """ 兑换结果通知 """
    @protocols.unpack_arguments(with_phone=False)
    def get(self):
        rate = options.get('rate')
        log_path = self.config['log']['duiba']
        error_path = self.config['log']['error']
        utils.loggers.use('duiba', log_path).info(self.request.uri)
        params = self.get_params()
        succ, msg = self.check_sign(params)
        if not succ:
            result = {"status": "fail", "message": "参数校验失败", "errorMessage": msg[1]}
            return self.write_json(result)

        order = orders.get_ex_order_ordernum(params['orderNum'])
        if not order or order['status'] in [13, 14]:
            utils.loggers.use('error', error_path).info(self.request.uri)
            return
        # 拒绝订单不退回积分
        #if order['status'] == 12:
        #    return self.write('ok')

        if params['success'].lower() == 'false':
            # 兑换失败，退回积分，增加流水
            orders.set_ex_order_status(params['orderNum'], orders.EXSTS_FAIL, params['errorMessage'])
            user_info = users.get_info(order['uid'])
            users.add_ex_points(user_info['uid'], order['points'])
            orders.new_global_order(
                order['uid'], user_info['points'], order['points'], orders.OTYPE_EXCHANGE,
                u"兑换失败，退回 %d 元" % int(order['points']/int(rate)))
        elif params['success'].lower() == 'true':
            orders.set_ex_order_status(params['orderNum'], orders.EXSTS_SUCC, params['errorMessage'])
        else:
            utils.loggers.use('error', error_path).info(self.request.uri)

        self.write('ok')

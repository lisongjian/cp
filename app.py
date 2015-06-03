#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author lisongjian@youmi.net
#
""" 主要逻辑 """

import torndb
import tornado.web
import db
import redis
import os.path
from protocols import JSONBaseHandler
#import wsgiserver as server
#import gevent.monkey
#gevent.monkey.patch_all()
import server
from service import user, feedback, task, duibaV2,version, question, callback, invite, adurl

try:
    import __pypy__
except ImportError:
    __pypy__ = None


class Application(server.Application):

    def startup(self):
        """处理各种数据库链接等

        比如:
            self.db = torndb.Connection(
                host=self.config.mysql_host, database=self.config.mysql_database,
                user=self.config.mysql_user, password=self.config.mysql_password)
        """
        #self.db = torndb.Connection(**self.config['mysql'])
        self.db = db.mysql = torndb.Connection(**self.config['mysql'])
        pool = redis.ConnectionPool(**self.config['redis'])
        self.redis = db.redis = redis.Redis(connection_pool=pool)


class MainHandler(JSONBaseHandler):

    def get(self):
        self.write_json({"d": "helloworld"})


if __name__ == '__main__':
    static_path = os.path.join(os.path.dirname(__file__), "static")

    handlers = [
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        # 广告回调
        (r"/callback/([^/]+)", callback.CallbackHandler),
        #(r"/callback", callback.CallbackHandler),
        # 用户邀请码
        (r"/user/uic", user.UicHandler),
        # 用户头像
        (r"/user/icon", user.IconHandler),
        # 账号注册
        (r"/user/sign", user.SignHandler),
        # 短信验证
        (r"/user/smscode", user.CodeHandler),
        # 账号登录
        (r"/user/login", user.LoginHandler),
        # 修改密码
        (r"/user/chpwd", user.ChpwdHandler),
        # 找回密码
        (r"/user/lostpwd", user.LostpwdHandler),
        # 忘记密码手机验证
        (r"/user/check_smscode", user.ChecksmsHandler),
        # 设备检测
        (r"/check_device", user.CheckDeviceHandler),
        # 绑定设备
        (r"/bind_device", user.DeviceHandler),
        # 用户详情
        #(r"/user/detail", user.DetailHandler),
        (r"/apprentices", user.DetailHandler),
        # 注销
        (r"/user/logout", user.LogoutHandler),
        # 找回密码验证
        (r"/user/lostpwdcode", user.LostpwdcodeHandler),
        # 新手任务列表
        (r"/novice_task", user.NewtaskHandler),
        # 用户配置
        (r"/user_config", user.UserConfigHandler),
        # 账户余额
        (r"/qbs", user.QbsHandler),
        # 明细记录
        (r"/qos", user.QosHandler),
        # 意见反馈
        (r"/feedback", feedback.FeedbackHandler),
        # 分享
        (r"/after_share", feedback.ShareHandler),
        # 获取屏保图url
        (r"/get_pics", task.GetpicHandler),
        # 第一张屏保图id
        (r"/get_adids", task.GetadHandler),
        # 今日解锁奖励任务列表
        (r"/get_unlock_tasks", task.GetUnlockHandler),
        # 解锁奖励
        (r"/unlock", task.UnlockHandler),
        # 兑换
        (r"/exchange", duibaV2.LoginHandler),
        (r"/duiba/consume", duibaV2.ConsumeHandler),
        (r"/duiba/notify", duibaV2.NotifyHandler),
        # 更新
        (r"/update",version.UpdateHandler),
        # F&Q
        (r"/FAQ",question.QuestionHandler),
        # 收徒
        #(r"/invite", invite.MyInviteHandler),
        # 分享
        (r"/share", invite.ShareHandler),
        # youmi广告回调
        (r"/ad/([^/]+)", adurl.AdyoumiHandler),

    ]

    if __pypy__:
        print("Running in PYPY")
    else:
        print("Running in CPython")

    server.mainloop(Application(handlers))

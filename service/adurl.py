#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

有米广告回调处理
 @author lisongjian@youmi.net

"""
import utils, datetime
from protocols import JSONBaseHandler
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class AdyoumiHandler(JSONBaseHandler):
    def get(self, platform):
        log_path = self.config['log']['adyoumi']
        utils.loggers.use('adyoumi', log_path).info(self.request.uri)
        if platform == 'qianlu':
            self.__save_qianlu_order()

    def __save_qianlu_order(self):
        params = {}
        log_path = self.config['log']['adyoumi']

        for key in ['imei', 'mac', 'callback_url']:
            params[key] = self.get_argument(key, "")
        mac = params['mac'].encode('utf-8')
        idfa = params['imei'].replace("-","").lower().encode('utf-8')
        #print token
        utils.loggers.use('adyoumi', log_path).info(params)
        idfa_info = self.db.get(
            "SELECT * FROM `wallad_clicks` WHERE `idfa`=%s LIMIT 1",idfa)
        if not idfa_info:
            utils.loggers.use('adyoumi', log_path).info("INSERT INTO `wallad_clicks` (idfa, mac, callback_url, adserver,create_time) VALUES (%s, %s, %s, %s, %s)" %
                        (idfa, mac, params['callback_url'], 1, datetime.datetime.now()))
            self.db.execute(
                "INSERT INTO `wallad_clicks` (idfa, mac, callback_url, adserver,create_time,appType)"
                "VALUES (%s, %s, %s, %s, %s,1)",
                idfa, mac, params['callback_url'], 1, datetime.datetime.now())
            self.return_success()
        else:
            self.write('already had imei')

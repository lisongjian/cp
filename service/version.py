#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenyongjian@youmi.net
#
"""更新信息相关

"""
import protocols
from models import version

class UpdateHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        data = version.get()
        update = {
            'url' : data[0]['url'],
            'version' : data[0]['version_code'],
            'update_message' : data[0]['update_message']
        }
        self.return_result(update)

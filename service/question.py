#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenyongjian@youmi.net
#
"""F & Q 相关

"""
import protocols
import utils
from models import question

class QuestionHandler(protocols.JSONBaseHandler):
    @protocols.unpack_arguments()
    def get(self):
        data = question.get()
        param = []
        for d in data:
            param.append({
                "answer" : d['answers'],
                "question" : d['questions']
            })
        print param
        self.return_result({"num":0,"list":param})

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

import os
import base64
import ujson as json
import utils

from hashlib import sha256
from hmac import HMAC

class SessionBase(dict):
    """ session基类"""

    def __init__(self, session_id, hmac_key):
        self.session_id = session_id
        self.hmac_key = hmac_key


class Session(SessionBase):
    """ session类 """

    def __init__(self, session_manager, request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler
        try:
            current_session = session_manager.get(request_handler)
        except InvalidSessionError:
            current_session = session_manager.get()
        for key, data in current_session.iteritems():
            self[key] = data
        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key
        self.save()

    def save(self):
        print self
        self.session_manager.set(self.request_handler, self)


class SessionManager(object):
    """ session操作类 """

    def __init__(self, secret, redis, timeout):
        self.secret = secret
        self.timeout = timeout
        self.redis = redis

    def get(self, request_handler=None):
        if request_handler == None:
            session_id = None
            hmac_key = None
        else:
            session_id = request_handler.get_cookie("session_id")
            hmac_key = request_handler.get_secure_cookie("verification")
        if session_id == None:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        else:
            session_exists = True

        if hmac_key != self._generate_hmac(session_id):
            raise InvalidSessionError()
        session = SessionBase(session_id, hmac_key)
        if session_exists:
            session_data = self._fetch(session_id)
            for key, data in session_data.iteritems():
                session[key] = data

        return session

    def set(self, request_handler, session):
        request_handler.set_cookie("session_id", session.session_id, expires_days=7)
        request_handler.set_secure_cookie("verification", session.hmac_key, expires_days=7)
        session_data = json.dumps(dict(session.items()))
        self.redis.setex(session.session_id, session_data, self.timeout)

    def _fetch(self, session_id):
        session_data = {}
        raw_data = self.redis.get(session_id)
        if raw_data != None:
            self.redis.setex(session_id, raw_data, self.timeout)
            session_data = json.loads(raw_data)
        return session_data

    def _generate_id(self):
        return utils.md5(base64.b64encode(os.urandom(64)))

    def _generate_hmac(self, session_id):
        result = session_id
        for i in xrange(3):
            result = HMAC(result, self.secret, sha256).hexdigest()
        return result


class InvalidSessionError(Exception):
    pass

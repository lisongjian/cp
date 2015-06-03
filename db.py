#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#

import ujson as json

mysql = None
redis = None

def db_cache(key, count=1, ttl=86400):
    """ 数据库缓存修饰器 """
    def db_cache_wrap(method):
        def wrapper(*args, **kwargs):
            key_name = "suoping:%s" % key
            for i in xrange(count):
                key_name += ':%s' % args[i]
            data = redis.get(key_name)
            if not data:
                data = method(*args, **kwargs)
                if data:
                    redis.setex(key_name, json.dumps(data), ttl)
            else:
                data = json.loads(data)
            return data
        return wrapper
    return db_cache_wrap


def del_cache(key, *args):
    key_name = "suoping:%s" % key
    for arg in args:
        key_name += ':%s' % arg
    redis.delete(key_name)

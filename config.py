#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/23 23:05
# @Author  : ChenHuan
# @Site    : 
# @File    : config.py
# @Desc    :
# @Software: PyCharm

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'product'

# PHANTOMJS配置,不加载图片,开启缓存
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

KEYWORDS = '美食'
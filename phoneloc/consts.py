#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

HEAD_FMT = "<4si"
PHONE_FMT = "<iiB"
DEFAULT_LOCID = '100000'
DEFAULT_CARRIER = "未知电信运营商"
DEFAULT_CARRIER_NO = 7
DAT_FILE = "phone.dat"
CSV_FILE = "phonedat.csv"
CARRIER2NO = {
    "移动": 1,
    "联通": 2,
    "电信": 3,
    "电信虚拟运营商": 4,
    "联通虚拟运营商": 5,
    "移动虚拟运营商": 6,
}
NO2CARRIER = {CARRIER2NO[k]: k for k in CARRIER2NO}

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import struct
from io import open

from .consts import (HEAD_FMT, PHONE_FMT, NO2CARRIER, DEFAULT_CARRIER,
                     DEFAULT_LOCID, DAT_FILE)


class PhoneLoc(object):
    def __init__(self, dat_file=None, locid_map=None):

        if dat_file is None:
            dat_file = os.path.join(os.path.dirname(__file__), DAT_FILE)

        with open(dat_file, 'rb') as f:
            self.buf = f.read()

        self.head_fmt = HEAD_FMT
        self.phone_fmt = PHONE_FMT
        self.head_fmt_length = struct.calcsize(self.head_fmt)
        self.phone_fmt_length = struct.calcsize(self.phone_fmt)
        self.version, self.first_idx_offset = struct.unpack(self.head_fmt, self.buf[:self.head_fmt_length])
        self.phone_record_count = (len(self.buf) - self.first_idx_offset) // self.phone_fmt_length
        if locid_map and os.path.isfile(locid_map):
            self._load_locid(locid_map)
            self.loaded_locid = True
        else:
            self.loaded_locid = False

    def phone_dat_msg(self):
        print("版本号:{}".format(self.version))
        print("总记录条数:{}".format(self.phone_record_count))

    @classmethod
    def _format_phone_content(cls, phone_num, record_content, phone_type):
        province, city, zip_code, area_code = record_content.split('|')
        return {
            "phone": phone_num,
            "province": province,
            "city": city,
            "zip_code": zip_code,
            "area_code": area_code,
            "phone_type": NO2CARRIER.get(phone_type, DEFAULT_CARRIER)
        }

    def _lookup_phone(self, phone_num):

        phone_num = str(phone_num)
        assert 7 <= len(phone_num) <= 11
        int_phone = int(str(phone_num)[0:7])

        left = 0
        right = self.phone_record_count
        buflen = len(self.buf)
        while left <= right:
            middle = (left + right) // 2
            current_offset = self.first_idx_offset + middle * self.phone_fmt_length
            if current_offset >= buflen:
                return

            buffer = self.buf[current_offset: current_offset + self.phone_fmt_length]
            cur_phone, record_offset, phone_type = struct.unpack(self.phone_fmt, buffer)

            if cur_phone > int_phone:
                right = middle - 1
            elif cur_phone < int_phone:
                left = middle + 1
            else:
                end_offset = self.buf.find(b'\x00', record_offset)
                record_content = self.buf[record_offset:end_offset]
                record_content = record_content.decode('utf8')
                return PhoneLoc._format_phone_content(phone_num, record_content, phone_type)

    def find(self, phone_num):
        phone_info = self._lookup_phone(phone_num)
        if self.loaded_locid:
            return self.text_to_loc(phone_info)
        return phone_info

    def text_to_loc(self, phone_info):
        if phone_info:
            locid = self.get_locid((phone_info['province'], phone_info['city']))
            phone_info['loc_id'] = locid
            return phone_info

    def get_locid(self, loc_text):
        if loc_text in self.to_locid:
            return self.to_locid[loc_text]
        return DEFAULT_LOCID

    def _load_locid(self, mapping_path):
        self.to_locid = {}
        with open(mapping_path, encoding='utf-8') as file_:
            for line in file_:
                row = line.strip().split(',')
                self.to_locid[tuple(row[1:])] = row[0]

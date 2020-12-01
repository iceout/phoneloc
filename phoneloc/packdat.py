#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import struct
from io import open

from .consts import (HEAD_FMT, PHONE_FMT, NO2CARRIER, CARRIER2NO,
                     DEFAULT_CARRIER_NO, CSV_FILE)


class DataConverter(object):

    def __init__(self, csv_file=None, dat_file=None, version=None):

        self.head_fmt = HEAD_FMT
        self.phone_fmt = PHONE_FMT
        self.head_fmt_length = struct.calcsize(self.head_fmt)
        self.phone_fmt_length = struct.calcsize(self.phone_fmt)

        self.csv_file = csv_file
        self.dat_file = dat_file
        self.dat_version = version
        if csv_file is None:
            self.csv_file = os.path.join(os.path.dirname(__file__), CSV_FILE)

    def pack(self):
        phonedat = []
        dat2offset = {}
        with open(self.csv_file, encoding='utf-8') as file_:
            for line in file_:
                row = line.strip().split(',')
                phone = int(row[0])
                carrier = CARRIER2NO.get(row[3], DEFAULT_CARRIER_NO)
                dat_str = "{}|{}|{}|{}\0".format(row[1], row[2], row[4], row[5]).encode('utf8')
                phonedat.append((phone, carrier, dat_str))
        phonedat.sort(key=lambda x: x[0])
        print("Version: ", self.dat_version)
        print("Count: ", len(phonedat))

        with open(self.dat_file, "wb") as FILE:
            data_buffer = []
            index_offset = self.head_fmt_length
            for phone, carrier, dat in phonedat:
                if dat in dat2offset:
                    continue
                dat2offset[dat] = index_offset
                index_offset = index_offset + len(dat)
                fmt = str(len(dat)) + "s"
                data_buffer.append(struct.pack(fmt, dat))

            self.first_idx_offset = index_offset
            header_buffer = struct.pack(self.head_fmt, self.dat_version.encode('utf-8'), self.first_idx_offset)

            FILE.write(header_buffer)
            for buffer in data_buffer:
                FILE.write(buffer)
            for phone, carrier, dat in phonedat:
                data_offset = dat2offset[dat]
                index_buffer = struct.pack(self.phone_fmt, phone, data_offset, carrier)
                FILE.write(index_buffer)

    def unpack(self):
        with open(self.dat_file, 'rb') as rfile_:
            buf = rfile_.read()
        version, first_idx_offset = struct.unpack(self.head_fmt, buf[:self.head_fmt_length])
        phone_record_count = (len(buf) - first_idx_offset) // self.phone_fmt_length
        print("Version: ", version)
        print("Count: ", phone_record_count)
        count = 0
        with open(self.csv_file, 'w') as file_:
            while count < phone_record_count:
                current_offset = first_idx_offset + count * self.phone_fmt_length
                buffer = buf[current_offset: current_offset + self.phone_fmt_length]
                phone, record_offset, phone_type = struct.unpack(self.phone_fmt, buffer)
                end_offset = buf.find(b'\x00', record_offset)
                record_content = buf[record_offset:end_offset]
                province, city, zip_code, area_code = record_content.decode('utf8').split('|')
                row = ','.join([str(phone), province, city, NO2CARRIER[phone_type],
                                zip_code, area_code])
                file_.write((row + '\n'))
                count += 1

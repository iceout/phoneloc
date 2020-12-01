#!/usr/bin/env python3
from __future__ import print_function, unicode_literals

from unittest import TestCase
from phoneloc.phoneloc import PhoneLoc


class Testphoneloc(TestCase):
    def setUp(self):
        self.pl = PhoneLoc()

    def test_find(self):

        info = self.pl.find('1858265')
        assert info['province'] == '四川'
        assert info['city'] == '西昌'
        assert info['phone_type'] == '联通'
        assert info['loc_id'] == '118338'

        info = self.pl.find('1860834')
        assert info['province'] == '四川'
        assert info['city'] == '凉山'
        assert info['phone_type'] == '联通'
        assert info['loc_id'] == '118338'

        info = self.pl.find('2900004')
        assert info is None

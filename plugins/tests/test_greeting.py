#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# あいさつ返す音声コマンド(greeting)をテストする

import unittest
from urllib.request import urlopen

from greeting import *

class TestGreeting(unittest.TestCase):

    def test_process(self):
        """
        process()をテストする
        """
        self.assertTrue(process("おはよう"), "お早うございます")

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 挨拶を返す音声コマンド

from random import choice
from datetime import datetime

def process(message, config):
    if "おはよう" in message:
        return "おはようございます"
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# ウィキペディアを検索する音声コマンド(wikipedia)をテストする

import unittest
from urllib.request import urlopen

from wikipedia import *

class TestWikipedia(unittest.TestCase):

    def test_get_wikipedia_srouce(self):
        """
        get_wikipedia_srouce()をテストする
        """
        # Wikipediaに存在する項目
        src = get_wikipedia_srouce('ももいろクローバーZ')
        self.assertTrue("早見あかり" in src)
        self.assertTrue("有安杏果" in src)

        # Wikipediaに存在しない項目
        src = get_wikipedia_srouce('ももいろクローバーX')
        self.assertEqual(len(src), 0)

    def test_get_wikipedia_srouce(self):
        """
        get_abstruction()をテストする
        """

        # WikipediaからHTMLを得る
        src = get_wikipedia_srouce('ジョゼフ・フーリエ')
        # 概要を得る
        abst = get_abstruction(src)
        self.assertEqual(abst,
                ("ジャン・バティスト・ジョゼフ・フーリエ男爵"
                 "は、フランスの数学者・物理学者。"))

        # WikipediaからHTMLを得る
        src = get_wikipedia_srouce('フーリエ')
        # 概要を得る
        abst = get_abstruction(src)
        self.assertEqual(abst,
                "フーリエ (Fourier) は、フランス語圏の姓。")

        # Wikipediaに存在しない項目
        src = get_wikipedia_srouce('ももいろクローバーX')
        # 概要を得る
        abst = get_abstruction(src)
        self.assertEqual(abst, '')


    def test_process(self):
        """
        process()をテストする
        """
        # 失敗するパターン
        self.assertEqual(process("有安杏果を検", None), "")

        self.assertEqual(process("有安杏果を検索",None),
                ("有安 杏果はももいろクローバーZの元メンバー、"
                 "グループでのイメージカラーは緑色であった。"))

        # Wikipediaに存在しない項目
        self.assertEqual(process("ももいろクローバーXを検索", None),
                "ももいろクローバーXという項目は検索できませんでした。")

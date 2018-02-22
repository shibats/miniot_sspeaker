#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 天気予報を返す音声コマンド(whaetherreport)をテストする

import unittest
from urllib.request import urlopen

from weatherreport import *

url = 'https://tenki.jp/week/3/16/'
src = urlopen(url).read().decode('utf-8')

class TestWeatherreport(unittest.TestCase):

    def test_get_table(self):
        """
        get_table()をテストする
        """
        # HTML全体からテーブルを取得
        table_body = get_table(src)
        # 取得した文字列がtableタグで囲まれているかどうか試す
        self.assertTrue(table_body.startswith('<table'))
        self.assertTrue(table_body.endswith('</table>'))


    def test_get_rows(self):
        """
        get_rows()をテストする
        """

        # HTML全体からテーブルを取得
        table_body = get_table(src)

        # tr要素を返す
        rows = get_rows(table_body)
        # 各trがtrタグで囲まれていて
        # 地点表示用のtdタグがあるかどうかを確かめる
        for tr in rows:
            self.assertTrue(tr.startswith('<tr>'))
            self.assertTrue(tr.endswith('</tr>'))
            self.assertTrue('<td class="point-name">' in tr)


    def test_get_element_from_tr(self):
        """
        get_element_from_tr()をテストする
        """

        # テスト用のtr要素
        tr = """<tr>
      <td class="point-name"><a href="/forecast/3/16/4410/13101-10days.html">千代田区</a><span class="city-name">東京地方(東京)</span></td>
      <td class="forecast-wrap">
        <p class="weather-icon"><img src="https://static.tenki.jp/images/icon/forecast-days-weather/08.png" alt="曇" title="曇" width="47" height="30"><br><span class="forecast-telop">曇</span></p>
        <p><span class="high-temp">6</span>/<span class="low-temp">2</span></p>
        <p class="precip">30<span class="unit">%</span></p>
      </td>
        """
        # 各要素を取得
        place, weather, htemp, ltemp, rperc = get_element_from_tr(tr)

        self.assertTrue(place, '千代田区')
        self.assertTrue(weather, '曇')
        self.assertTrue(htemp, '6')
        self.assertTrue(ltemp, '2')
        self.assertTrue(place, '30')
        
        # 要素の欠落したパターンをテスト
        tr2 = """<tr>
      <td class="point-name"></td>
      <td class="forecast-wrap">
        <p class="weather-icon"><img src="https://static.tenki.jp/images/icon/forecast-days-weather/08.png" alt="曇" title="曇" width="47" height="30"><br><span class="forecast-telop">曇</span></p>
        <p><span class="low-temp">2</span></p>
        <p class="precip">30<span class="unit">%</span></p>
      </td>
        """

        # 各要素を取得
        place, weather, htemp, ltemp, rperc = get_element_from_tr(tr)

        self.assertTrue(place, '')
        self.assertTrue(weather, '曇')
        self.assertTrue(htemp, '')
        self.assertTrue(ltemp, '2')
        self.assertTrue(place, '30')
        



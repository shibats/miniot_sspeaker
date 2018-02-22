#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 天気予報を返す音声コマンド

import re
from urllib.request import urlopen
from datetime import date

# スクレイピング用の正規表現パターン
re_flag = re.S | re.M
# table抽出のパターン
table_pat = re.compile(r'(<table.+?</table>)', re_flag)
# tr抽出のパターン
tr_pat = re.compile(r'(<tr>.+?</tr>)', re_flag)
# td抽出のパターン
td_pat = re.compile(r'<td.+?>(.+?)</td>', re_flag)
# 地点抽出のパターン
place_pat = re.compile(r'<a.+?>(.+?)</a>', re_flag)
# 天気抽出のパターン
weather_pat = re.compile((r'<p class="weather-icon">.+?<span.+?>'
                           '(.+?)</span></p>'),
                           re_flag)
# 最高気温，最低気温
htemp_pat = re.compile(r'<span class="high-temp">(.+?)</span>',
                           re_flag)
ltemp_pat = re.compile(r'<span class="low-temp">(.+?)</span>',
                           re_flag)
# 降水確率
rperc_pat = re.compile(r'<p class="precip">(.+?)<span',
                           re_flag)


def process(message, config):
    """
    Webから天気予報を取得，文字列を構築して返す
    config.WR_URL, config.WR_INDEXを使って天気予報を取得する
    """

    #try:
    if 1:
        # 天気予報のHTMLソースを取得
        src = urlopen(config.WR_URL).read().decode('utf-8')
        if len(src) < 100:
            raise Exception('Source is to short')

        # HTML全体からテーブルを取得
        table_body = get_table(src)
        if len(src) < 100:
            raise Exception('Source is to short')

        # tr要素を取得
        rows = get_rows(table_body)

        # 天気予報の要素を取得
        t_tr = rows[config.WR_INDEX]
        place, weather, htemp, ltemp, rperc = get_element_from_tr(t_tr)

        # 要素を使って文字列を組み立てる
        # 本日の日付を取得
        td = date.today()
        wr = ("{0}の{1}月{2}日の天気は、{3}、"
              "最高気温は{4}、最低気温は{5}、"
              "降水確率は{6}パーセントでしょう").format(
                    place, td.month, td.day, weather, htemp, ltemp, rperc)
        return wr

    #except:
    #    return ("天気予報取得時にエラーが発生しました。"
    #            "設定を確認してください") 


def get_table(src):
    """
    天気予報のHTML全体を含む文字列(src)を受けて
    天気予報のテーブル部分だけを返す関数
    """
    return ''.join(table_pat.findall(src))


def get_rows(table_src):
    """
    天気予報のテーブルから，予報の入ったtr要素を取り出す
    結果は文字列のリストとして返す
    """
    trs = tr_pat.findall(table_src)
    if trs:
        return trs[1:]
    return []


def get_element_from_tr(tr_src):
    """
    予報の入ったtr要素から，要素を取り出して文字列として返す
    地区名，天気，最高気温，最低気温，降水確率
    の順に文字列のリストを返す
    """
    # tdを抽出
    tds = td_pat.findall(tr_src)
    if len(tds) < 2:
        return ['', '', '', '', '']
    # 地区名を取得
    place = ''.join(place_pat.findall(tds[0]))
    # 天気を取得
    weather = ''.join(weather_pat.findall(tds[1]))
    # 最高気温，最低気温を取得
    htemp = ''.join(htemp_pat.findall(tds[1]))
    ltemp = ''.join(ltemp_pat.findall(tds[1]))
    # 降水確率を取得
    rperc = ''.join(rperc_pat.findall(tds[1]))

    return [place, weather, htemp, ltemp, rperc]


if __name__ == '__main__':
    class Klass:
        pass

    k = Klass()
    k.WR_URL = 'https://tenki.jp/week/3/17/'
    k.WR_INDEX = 0
    r = process('', k)
    print(r)



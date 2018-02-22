#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# ウィキペディアを検索する音声コマンド

import re
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote

# WikipediaのベースURL
url_base = 'https://ja.wikipedia.org/wiki/'

# スクレイピング用の正規表現パターン
re_flag = re.S | re.M
# pエレメントを取得するパターン
p_pat = re.compile(r'<p>(.+?)</p>', re_flag)
# タグを除去するためのパターン
removetag_pat = re.compile(r'<.+?>', re_flag)
# 丸括弧，角括弧を除去するためのパターン
removeblackets_pat = re.compile(r'\[.+?\]', re_flag)
removeblackets_pat2 = re.compile(r'（.+?）', re_flag)


def process(message, config):
    # 「〜を検索」という命令を受けて，Wikipediaを
    if message.endswith('を検索'):
        # Wikipedia検索を実行
        word = message.replace('を検索', '')
        src = get_wikipedia_srouce(word)
        if not src:
            return word+"という項目は検索できませんでした。"
        r = get_abstruction(src)
        if r:
            # 結果が帰ってきたので，取得した概要を返す
            return r
    return ''



def get_wikipedia_srouce(word):
    """
    語を与えてWikipediaにアクセス，HTMLのソースを取得して
    文字列として返す
    """
    # URLを生成
    url = url_base+quote(word)
    try:
        # HTMLを取得
        robj = urlopen(url)
        # HTMLを返す
        return robj.read().decode('utf-8')
    except HTTPError as e:
        if e.code >= 400:
            return ''
        return ''


    return src


def get_abstruction(src):
    """
    Wikipediaの検索結果(HTML)から概要を得る
    最初のpエレメントからHTMLのタグを除去して返す
    """
    # 最初のpエレメントを取得する
    p_elems = p_pat.findall(src)
    if p_elems:
        p_elem = p_elems[0]
        # タグを除去する
        abst = removetag_pat.sub('', p_elem)
        # 丸括弧，角括弧を除去する
        abst = removeblackets_pat.sub('', abst)
        abst = removeblackets_pat2.sub('', abst)
        return abst
    return ''


if __name__ == '__main__':
    src = get_wikipedia_srouce('ももいろクローバーX')
    if not src:
        print("pass")
    print(src)
    r = get_abstruction(src)
    print('-'*40)
    print(r)



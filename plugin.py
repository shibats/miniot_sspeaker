#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__all__ = ['import_commands', 'invoke_commands']

import sys
import os
import importlib
import traceback
import logging


COMMANDS = []


def import_commands(p='plugins'):
    """
    コマンド用のプラグインを読み込む
    """

    # プラグインディレクトリのパスを設定
    base = os.path.dirname(__file__)
    plugin_path = os.path.join(base, p)

    # プラグインの一覧を取得
    dirs = os.listdir(plugin_path)

    # プラグインのリストをクリア
    COMMANDS.clear()

    # プラグインを動的にインポート
    for pfn in dirs:
        if pfn.startswith('_'):
            continue
        pfn = pfn.replace('.py', '')
        mod = importlib.import_module(p+'.'+pfn)
        # プラグイン保存用のリストにモジュールオブジェクトを追加
        COMMANDS.append(mod)


def invoke_commands(w, config):
    """
    プラグインから読み込んだコマンドを実行する
    """

    # すべてのプラグインに認識したワードを渡し，コマンドを実行する
    for mod in COMMANDS:
        try:
            if hasattr(mod, 'process'):
                mon_r = mod.process(w, config)
                if mon_r:
                    # 戻り値が戻ったら，その値をそのまま返す
                    return mon_r
        except:
            e = e = sys.exc_info()[0]
            msg = "コマンド実行中にエラーが発生しました\n{}"
            logging.error(msg.format(traceback.format_tb(e)))
    # プラグインが反応しなかったので，Noneを返す
    return None



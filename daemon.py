#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 標準ライブラリのモジュールをインポート

import sys
import os
from io import BytesIO
import logging
import optparse
import importlib

# PyAudio，gttsなど外部ライブラリをインポート

import pyaudio
from gtts import gTTS

# PyGameをインポート

pygame_ready = False
try:
    import pygame
    pygame.mixer.init()
    pygame_ready = True
except ImportError:
    pass


from audio import AudioData, AudioFile
from record import get_sound_chunk
from plugin import invoke_commands, import_commands


def get_audiodata():
    """
    設定に従って音声を録音，AudioDataオブジェクトとして返す
    """
    sf = BytesIO()
    sf, w = get_sound_chunk(pyaudio.paInt16, 1,
                         config.SAMPLE_RATE, sf,
                         config.VOLUME_THRESHOLD,
                         config.STARTUP_TIME,
                         config.SILENCE_LIMIT,
                         config.PREV_LENGTH,
                         config.MAX_SECOND)

    sf.seek(0)
    ad = AudioData(sf.read(), 16000, w)

    msg = "音声チャンクを取得しました(サイズ{}バイト)。"
    logging.debug(msg.format(len(ad.get_raw_data())))

    return ad


def recognize(ad):
    """
    設定に従い音声認識を実行，結果を返す
    """
    # 音声認識オブジェクトを生成
    rg = config.RECOGNIZER()
    # 音声認識を実行
    result = rg.recognize(ad, config, show_all=False)
    msg = "音声認識を実行しました。\n{}"
    logging.debug(msg.format(str(result)))
    return result


def speech(txt):
    """
    テキストを音声ファイルに変換して再生する
    """
    # gttsを使って音声合成を実行
    so = gTTS(text=txt, lang="ja")
    so.save('speech_text.mp3')
    if pygame_ready:
        # PyGameをインポートしていたら，PyGameを使って音声再生
        pygame.mixer.music.load('speech_text.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # 音声の再生が終わるまで待つ
            pygame.time.Clock().tick(5)
    else:
        # PyGameをインポートできなかったので
        # コマンドを使って音声再生(Raspberry Piのみ)
        os.system("omxplayer ./speech_text.mp3")
    os.remove('./speech_text.mp3')


def play_sound(path):
    """
    ファイルを指定して音声を再生する
    """
    if pygame_ready:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # 音声の再生が終わるまで待つ
            pygame.time.Clock().tick(5)


def restart():
    """
    プラグインと設定ファイルを再読み込みする
    """
    import_commands()
    importlib.reload(config)


def run():
    """
    スマートスピーカーを動かす関数
    """
    logging.debug("スマートスピーカーを起動しました")
    play_sound(config.STARTUP)
    while True:
        # メインループ
        
        # 音声チャンクを取得する
        ad = get_audiodata()

        # 音声認識を実行
        result = recognize(ad)

        if result == config.WAKE_WORD:
            # ウェイクワードが発声されたので，コマンドを待ち受け
            msg = "ウェイクワードを認識しました({})"
            logging.debug(msg.format(config.WAKE_WORD))
            play_sound(config.COMMANDREADY)

            ad = get_audiodata()
            # 音声認識を実行
            result = recognize(ad)

            # 再起動，終了のコマンドを実行
            if result == '再起動':
                # 再起動コマンドを実行
                msg = ("スマートスピーカーを再起動し、"
                       "プラグインと設定ファイルを再読み込みします")
                logging.debug(msg)
                speech(msg)
                restart()
                continue
            elif result == '終了':
                # 終了コマンドを実行
                msg = "スマートスピーカーを終了します"
                logging.debug(msg)
                speech(msg)
                break

            # 音声コマンドを実行
            com_result = invoke_commands(result, config)

            if com_result:
                # 文字列を音声に変換して再生
                msg = "音声コマンドから以下の応答が返ってきました。\n{}"
                logging.debug(msg.format(com_result))
                speech(com_result)
            else:
                result_str = result
                if result_str:
                    msg = result_str+"はコマンドとして認識できません。"
                else:
                    msg = "音声認識に失敗しました。"
                play_sound(config.FAILURE)
                logging.debug(msg)
                speech(msg)


def set_option():
    """
    コマンド引数からいろいろな設定をする関数
    """
    parser = optparse.OptionParser()
    parser.add_option('-l', '--loglevel',
                      action='store', dest='loglevel', default='none',
                      help='ログレベルを設定する(DEBUG, INFO, WARNING, ERROR)')
    parser.add_option('-c', '--config',
                      action='store', dest='conffile', default='config',
                      help='設定ファイルを指定する(オプション，省略するとconfig.pyを使う)')
    options, remainder = parser.parse_args()
    loglevel = None
    if options.loglevel.lower() == 'debug':
        loglevel=logging.DEBUG
    elif options.loglevel.lower() == 'info':
        loglevel=logging.INFO
    if loglevel:
        logging.basicConfig(level=loglevel)

    # 設定ファイルを読み込む
    conffile = options.conffile
    global config   # 設定オブジェクト
    config = importlib.import_module(conffile)


if __name__ == '__main__':
    set_option()
    import_commands()
    run()


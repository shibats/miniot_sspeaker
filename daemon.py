#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from io import BytesIO
import logging
import optparse
import importlib

import pyaudio
from gtts import gTTS

import config
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
    result = rg.recognize(ad, config, show_all=True)
    msg = "音声認識を実行しました。\n{}"
    logging.debug(msg.format(str(result)))
    return result


def speech(txt):
    """
    テキストを音声ファイルに変換して再生する
    """
    so = gTTS(text=txt, lang="ja")
    so.save('speech_text.mp3')
    os.system("omxplayer ./speech_text.mp3")
    #os.remove('./speech_text.mp3')


def play_sound(path):
    """
    ファイルを指定して音声を再生する
    """
    os.system("aplay "+path)


def restart():
    """
    プラグインと設定ファイルを再読み込みする
    """
    import_commands()
    importlib.reload(config)
    print(config.MAX_SECOND)


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

        if (result.get('RecognitionStatus', '') == 'Success' and
            result.get('DisplayText', '') == config.WAKE_WORD ):
            # ウェイクワードが発声されたので，コマンドを待ち受け
            msg = "ウェイクワードを認識しました({})"
            logging.debug(msg.format(config.WAKE_WORD))
            play_sound(config.COMMANDREADY)

            ad = get_audiodata()
            # 音声認識を実行
            result = recognize(ad)

            # 再起動，終了のコマンドを実行
            if result.get('DisplayText', '') == '再起動':
                # 再起動コマンドを実行
                msg = ("スマートスピーカーを再起動し、"
                       "プラグインと設定ファイルを再読み込みします")
                logging.debug(msg)
                speech(msg)
                restart()
                continue
            elif result.get('DisplayText', '') == '終了':
                # 終了コマンドを実行
                msg = "スマートスピーカーを終了します"
                logging.debug(msg)
                speech(msg)
                break

            # 音声コマンドを実行
            com_result = invoke_commands(result.get('DisplayText', ''), config)

            if com_result:
                # 文字列を音声に変換して再生
                msg = "音声コマンドから以下の応答が返ってきました。\n{}"
                logging.debug(msg.format(com_result))
                speech(com_result)
            else:
                result_str = result.get('DisplayText', '')
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
    options, remainder = parser.parse_args()
    loglevel = None
    if options.loglevel.lower() == 'debug':
        loglevel=logging.DEBUG
    elif options.loglevel.lower() == 'info':
        loglevel=logging.INFO
    if loglevel:
        logging.basicConfig(level=loglevel)


if __name__ == '__main__':
    set_option()
    import_commands()
    run()


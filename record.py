#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import math
from io import BytesIO
import wave
import audioop
from collections import deque
import logging

import pyaudio


def get_chunk(rate):
    """
    サンプリングレートからチャンク値を得る
    """
    rate_chunk = {16000: 1024,
                  44100: 256}
    if rate in rate_chunk:
        return rate_chunk[rate]
    else:
        256

def audio_int(format, channels, rate, num_samples=50):
    """
    音をサンプリングして，環境音などを含めた
    ボリュームの平均を計算して返す
    """

    chunk = get_chunk(rate)

    audio = pyaudio.PyAudio()

    stream = audio.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    values = [math.sqrt(abs(audioop.avg(stream.read(chunk), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    stream.close()
    audio.terminate()
    logging.debug("測定中のボリューム平均値 : {}".format(r))
    return r


def get_sound_chunk(format, channels, rate,
                    fileobject,
                    threshold=200,
                    startup_time=2,
                    silence_limit=1,
                    prev_length=0.5,
                    max_second=9.5):
    """
    マイクからの音声を記録し，生データとサンプルサイズを返す
    format, channels, rateに
    PyAudioのストリーム用のパラメーターを引数として渡す
    音量が閾値(threshold)を超えたら録音を開始する
    startup_time回以上，チャンクが音量が閾値を超えたら録音開始を始める
    silence_limitの秒数間隔が空いたら録音を停止する
    prev_lengthの秒数分，録音開始前の音声を追加する
    録音の秒数がmax_secondに達するまで録音を続ける
    """

    chunk = get_chunk(rate)

    #PyAudioのストリームを開く
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    # 音声を取得開始
    msg = "閾値({})で音声のモニターを開始します"
    logging.debug(msg.format(threshold))

    audio2send = []
    cur_data = ''
    rel = rate/chunk
    slid_win = deque(maxlen=int(silence_limit*rel))
    prev_audio = deque(maxlen=int(prev_length*rel)) 
    started = False
    start_time = 0

    while True:
        # 音声データを読み込む
        cur_data = stream.read(chunk)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        if sum([x > threshold for x in slid_win]) > startup_time:
            # 音の大きさが閾値を超えた状態の処理
            if not started:
                # 開始フラグが立っていないので立てる
                started = True
                start_time = time.time()
                logging.debug("音声の記録を開始します")
            audio2send.append(cur_data)
            if time.time() - start_time >= min(9.5, max_second):
                # 録音時間がmax_secondか9.5秒を超えたので停止する
                break
        elif started:
            break
        else:
            prev_audio.append(cur_data)
    msg = "音声の記録を停止します。記録時間は{:.4f}秒でした"
    logging.debug(msg.format(time.time() - start_time))

    width = 0
    if started:
        save_sound(fileobject, list(prev_audio)+audio2send, audio, rate)
        width = audio.get_sample_size(pyaudio.paInt16)


    stream.close()
    audio.terminate()

    return fileobject, width

def save_sound(fileobject, data, p, rate):
    """
    音声をファイルオブジェクトに保存する
    """

    # writes data to WAV file
    data = b''.join(data)
    wf = wave.open(fileobject, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()


def test_record(key, rate=16000):
    import config

    logging.basicConfig(level=logging.DEBUG)

    from audio import AudioData, AudioFile
    from bing_recognizer import Bing
    threshold = audio_int(pyaudio.paInt16, 1, rate, 15)
    sf = BytesIO()
    sf, w = get_sound_chunk(pyaudio.paInt16, 1, rate, sf,
                         threshold*1.2,
                         config.STARTUP_TIME,
                         config.SILENCE_LIMIT,
                         config.PREV_LENGTH,
                         config.MAX_SECOND)

    sf.seek(0)
    ad = AudioData(sf.read(), 16000, w)
    bs = Bing()
    r = bs.recognize(ad, key=key, show_all=True)
    print(r)


def get_threshold():
    import config
    print("閾値を測定します。静かにして少々お待ちください。")
    threshold = audio_int(pyaudio.paInt16, 1, config.SAMPLE_RATE, 30)
    print("閾値は{}です。".format(int(threshold*1.2)))


def save_test(fn, rate=16000):
    """
    音声をファイルオブジェクトに保存する
    """

    import config

    logging.basicConfig(level=logging.DEBUG)

    from audio import AudioData, AudioFile
    from bing_recognizer import Bing
    threshold = audio_int(pyaudio.paInt16, 1, rate, 15)
    sf = BytesIO()
    sf, w = get_sound_chunk(pyaudio.paInt16, 1, rate, sf,
                         threshold*1.2,
                         config.STARTUP_TIME,
                         config.SILENCE_LIMIT,
                         config.PREV_LENGTH,
                         config.MAX_SECOND)

    sf.seek(0)
    f = open(fn, 'wb')
    f.write(sf.read())
    f.close()


if __name__ == '__main__':
    test_record()


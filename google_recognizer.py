#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# google_recognizer.py
# Google Cloud Speech APIを使って音声認識をするクラス


import argparse
import base64
import json

from googleapiclient import discovery
import httplib2

DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')

class Google:

    def __init__(self):
        pass


    def recognize(self, audio_data, config=None, key='',
                  language="ja-JP", show_all=False):
        """
        Google Cloud Speech APIを使って音声認識を実行するメソッド。
        audio_data(AudioData)に音声ファイル，
        configに設定オブジェクト，keyにAPI Keyを渡して呼び出すと，
        APIを呼び出して結果を返す。
        show_allがTrueだとレスポンスのJSONを辞書に変換して返す。
        Falseだと，認識した文字列を返す。
        """
        print(show_all)
        # アクセスキーを変数に代入
        access_key = key or config.GOOGLE_KEY


        # WAVデータを変換，BASE 64エンコードする
        wav_data = audio_data.get_wav_data(
            convert_rate=16000,  # audio samples must be 8kHz or 16 kHz
            convert_width=2  # audio samples should be 16-bit
        )
        speech_data = base64.b64encode(wav_data)
        http = httplib2.Http()
        service = discovery.build('speech', 'v1beta1', http=http,
                        discoveryServiceUrl=DISCOVERY_URL,
                        developerKey=access_key)

        # APIに送るリクエストを作る
        service_request = service.speech().syncrecognize(
            body={
                'config': {
                    'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
                    'sampleRate': 16000,  # 16 khz
                    'languageCode': language
                },
                'audio': {
                    'content': speech_data.decode('UTF-8')
                    }
                })
        # APIを呼び出して結果を得る
        response = service_request.execute()

        # 結果を返す
        if show_all:
            return response
        else:
            if response.get('results', '') and \
                    len(response.get('results', [])) and\
                        len(response['results'][0].get('alternatives', [])):
                alt = response['results'][0]['alternatives'][0]
                if alt.get('transcript', ''):
                    return alt['transcript']
            return ""

def test_recognize(key, filename):
    """
    Google Cloud Speech APIを使って音声認識するテスト用関数
    """
    from audio import AudioData, AudioFile
    af = AudioFile(filename)
    af.__enter__()
    ad = AudioData(open(filename, 'rb').read(), 
                   af.SAMPLE_RATE, af.SAMPLE_WIDTH)
    gs = Google()
    r = gs.recognize(ad, key=key, show_all=True)
    print(r)

if __name__ == '__main__':
    import sys
    from audio import AudioData, AudioFile

    if len(sys.argv) > 2:
        test_recognize(sys.argv[1], sys.argv[2])


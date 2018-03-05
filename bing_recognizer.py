#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import uuid
import io
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class RequestError(Exception): pass


class UnknownValueError(Exception): pass


class Bing:

    def __init__(self):
        self.operation_timeout = None  # seconds after an internal operation 

    def recognize(self, audio_data, config=None, key='',
                  language="ja-JP", show_all=False):
        """
        Microsoft Bing Speech APIを使って音声認識を実行するメソッド。
        audio_data(AudioData)に音声ファイル，
        configに設定オブジェクト，keyにAPI Keyを渡して呼び出すと，
        APIを呼び出して結果を返す。
        show_allがTrueだとレスポンスのJSONを辞書に変換して返す。
        Falseだと，認識した文字列を返す。
        """

        # キャッシュしたaccess_tokenとexpire_timeを取り出す
        access_token, expire_time = getattr(self, "bing_cached_access_token", None), getattr(self, "bing_cached_access_token_expiry", None)
        allow_caching = True
        from time import monotonic
        if expire_time is None or monotonic() > expire_time:
            # キャッシュが無効の場合，access_tokenなどを取得する
            credential_url = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken"
            credential_request = Request(credential_url, data=b"", headers={
                "Content-type": "application/x-www-form-urlencoded",
                "Content-Length": "0",
                "Ocp-Apim-Subscription-Key": key or config.BING_KEY,
            })

            if allow_caching:
                start_time = monotonic()

            try:
                credential_response = urlopen(credential_request, timeout=60)
            except HTTPError as e:
                raise RequestError("credential request failed: {}".format(e.reason))
            except URLError as e:
                raise RequestError("credential connection failed: {}".format(e.reason))
            access_token = credential_response.read().decode("utf-8")

            if allow_caching:
                # access_tokenを保存する
                self.bing_cached_access_token = access_token
                self.bing_cached_access_token_expiry = start_time + 600  # according to https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoicerecognition, the token expires in exactly 10 minutes

        # wavのデータを，APIがサポートした形式にコンバートする
        wav_data = audio_data.get_wav_data(
            convert_rate=16000,  # audio samples must be 8kHz or 16 kHz
            convert_width=2  # audio samples should be 16-bit
        )

        url = "https://speech.platform.bing.com/speech/recognition/interactive/cognitiveservices/v1?{}".format(urlencode({
            "language": language,
            "locale": language,
            "requestid": uuid.uuid4(),
        }))

        if sys.version_info >= (3, 6):
            # Python 3.6以上の場合，
            # chunked-transferリクエストを使いAPIを呼び出す
            request = Request(url, data=io.BytesIO(wav_data), headers={
                "Authorization": "Bearer {}".format(access_token),
                "Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate=16000",
                "Transfer-Encoding": "chunked",
            })
        else:
            # Python 3.6以下の場合，POSTでAPIを呼び出すする
            ascii_hex_data_length = "{:X}".format(len(wav_data)).encode("utf-8")
            chunked_transfer_encoding_data = ascii_hex_data_length + b"\r\n" + wav_data + b"\r\n0\r\n\r\n"
            request = Request(url, data=chunked_transfer_encoding_data, headers={
                "Authorization": "Bearer {}".format(access_token),
                "Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate=16000",
                "Transfer-Encoding": "chunked",
            })

        try:
            response = urlopen(request, timeout=self.operation_timeout)
        except HTTPError as e:
            raise RequestError("recognition request failed: {}".format(e.reason))
        except URLError as e:
            raise RequestError("recognition connection failed: {}".format(e.reason))
        response_text = response.read().decode("utf-8")
        result = json.loads(response_text)

        # 結果を返す
        if show_all: return result
        if "RecognitionStatus" not in result or result["RecognitionStatus"] != "Success" or "DisplayText" not in result: raise UnknownValueError()
        print(result)
        return result["DisplayText"]


def test_recognize(key, filename):
    """
    Microsoft Bing Speech APIを使って音声認識するテスト用関数
    """
    from audio import AudioData, AudioFile
    af = AudioFile(filename)
    af.__enter__()
    ad = AudioData(open(filename, 'rb').read(), 
                   af.SAMPLE_RATE, af.SAMPLE_WIDTH)
    bs = Bing()
    r = bs.recognize(ad, key=key, show_all=True)
    print(r)

if __name__ == '__main__':
    import sys
    from audio import AudioData, AudioFile

    if len(sys.argv) > 2:
        test_recognize(sys.argv[1], sys.argv[2])

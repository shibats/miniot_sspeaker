# システムの設定値

from bing_recognizer import Bing

SAMPLE_RATE = 16000
VOLUME_THRESHOLD = 200
STARTUP_TIME = 3
SILENCE_LIMIT = 2
PREV_LENGTH = 1.0
MAX_SECOND = 9.5

WAKE_WORD = 'ラズパイ'

RECOGNIZER = Bing
BING_KEY = '(Bing Speech APIのキー)'

# 天気予報用のURLとインデックス

WR_URL = 'https://tenki.jp/week/3/'
WR_INDEX = 0

# 効果音

# 起動音
STARTUP = './sounds/startup.mp3'
# ウェイクワード認識，コマンド待ち
COMMANDREADY = './sounds/commandready.mp3'
# コマンド認識失敗
FAILURE = './sounds/failure.mp3'


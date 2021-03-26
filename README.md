# yasumi
Discord Bot for CoC7th, NanjaMonja, SmallTalk.

## Overview
仲間内でのセッション/雑談用のBotです.
- CoCのオンラインセッションのサポート
- ナンジャモンジャゲームのオンラインセッションのサポート
- 汎用ボイス再生/チャット機能

## Install

1. Bot本体の導入
'''sh
git clone https://github.com/satoh154/yasumi.git
conda env create -f environment.yml
conda activate yasumi

2. Google APIの設定
    1. Google Developers Consoleでプロジェクト作成
    2. Google Sheets APIを有効化
    3. OAuth用クライアントIDを作成し認証情報が書かれたjsonファイルをダウンロード

3. キャラクターシートの作成(CoC)
    1. スプレッドシートでキャラクターシートを作成(template[1])
    [1]:https://docs.google.com/spreadsheets/d/14-e4itrOXrGifIV3Y7X9d5Yr1HNzIIVM6WIAg1tAd_4/edit?usp=sharing
    2. スプレッドシートの共有アドレスにjsonファイルのe-mailアドレスを追加

4. 使用したい画像ファイルを`nanjamonja/images/`に保存(ナンジャモンジャ)

5. 使用したい音声ファイルを`sound/`に保存
    
5. Discord Botを作成しチャンネルに追加

6. コンフィグファイルの作成
以下のような`config.json`を作成し`main.py`と同じディレクトリに保存
'''json
{
    "json_file": "file name for json Google-API-key",
    "doc_id": "id of the spreadsheet used in the CoC",
    "client_id": "discord bot token",
    "sound": {
        "command to use for sound playback": "path to sound file"
    }
}

6. ffmpegのインストール

## Usage

Botのヘルプを参照してください.
`/yasumi init [coc|nanjamonja|free]`: イニシャライズ
`/yasumi help`: メインコマンドのヘルプを表示
`/yasumi help [coc|nanjamonja|free|sound]`: システムコマンドのヘルプを表示


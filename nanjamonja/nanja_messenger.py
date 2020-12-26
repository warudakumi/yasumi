import re
import random
from glob import glob
from collections import OrderedDict

from parse import parse, search
import numpy as np
import discord


class NanjaMessenger():

    def __init__(self):
        self.gamemode = 'matchmake'

        # players -> {name: list of keep_monster_id}
        self.players = OrderedDict()

        # monsters -> {id: dict of monster info({img_path: name})}
        self.monsters = {}

        image_paths = []
        for img in ('nanjamonja/images/*.png', 'nanjamonja/images/*.jpg'):
            image_paths.extend(glob(img))
        for idx, img_path in enumerate(image_paths):
            self.monsters[idx] = {'img_path': img_path, 'name': None}

        self.deck = [i for i in range(5) for i in range(len(self.monsters))]
        random.shuffle(self.deck)

        self.onfield = None
        self.pool = []


    def call(self, input_msg, player):
        if self.gamemode == 'matchmake':
            if input_msg.startswith('/join'):
                return self.__register_player(player)
            elif input_msg.startswith('/close'):
                return self.__close_register()
            else:
                return None
        elif self.gamemode == 'ongoing':
            if input_msg.startswith('/turn'):
                return self.__turn_up()
            elif input_msg.startswith('/name'):
                return self.__name(input_msg)
            elif input_msg.startswith('/trash'):
                return self.__trash()
            elif input_msg.startswith('/pick'):
                return self.__pick(player)
            elif input_msg.startswith('/status'):
                return self.__show_status()
            elif input_msg.startswith('/record'):
                return self.__show_record()
            elif input_msg.startswith('/help'):
                return self.__show_help()
            elif input_msg.startswith('/list'):
                return [self.__show_monster(monster) for monster in self.monsters.values()]
            return None


    def __register_player(self, player):
        self.players[player] = []
        msg = player + 'をプレイヤーとして登録したわ'
        return msg


    def __close_register(self):
        self.gamemode = 'ongoing'

        items = self.players.items()
        random.shuffle(items)
        self.players = OrderedDict(items)

        msg = '登録を締め切ったわ，順番はこんな感じね\n'
        for idx, name in enumerate(self.players.keys()):
            ordermsg = str(idx+1) + ': ' + name + '\n'
            msg += ordermsg
        msg += '準備できたら手番のプレイヤーは`/turn`と入力するのよ'
        return msg


    def __turn_up(self):
        if self.onfield:
            msg = 'すでにカードが盤上にあるわ' 
        elif not self.deck:
            msg = '山札が無くなっているわ\n'\
                    '次のゲームを始めるのなら`/yasumi nanjamonja`でリブートして頂戴'
        else:
            self.onfield = self.deck.pop(0)
            monster = self.monsters[self.onfield]
            img_path = monster['img_path']
            msg = ('', discord.File(img_path)) 
        return msg


    def __name(self, input_msg):
        if not self.onfield:
            msg = 'カードが盤上にないわ'
        else:
            input_msg = input_msg.replace('|', '')
            parsed_input_msg, = parse('/name {}', input_msg).fixed

            if self.monsters[self.onfield]['name'] is None:
                self.monsters[self.onfield]['name'] = parsed_input_msg
                self.pool.append(self.onfield)
                self.onfield = None
                msg = '命名したわ\n'\
                    '今のところ捨札は**' + str(len(self.pool)) + '**枚ね'
            else:
                msg = 'そのカードにはすでに名前が付けられているわ\n'\
                        '分からないのなら`/trash`で次に進めるか\n'\
                        '`/hint`で確認することね'
        return msg


    def __trash(self):
        if not self.onfield:
            msg = 'カードが盤上にないわ'
        else:
            self.pool.append(self.onfield)
            self.onfield = None
            msg = '捨札に移したわ\n'\
                    '今のところ捨札は**' + str(len(self.pool)) + '**枚ね\n'
            if len(self.deck) == 1:
                msg += 'ちなみに次が最後のカードよ'
        return msg


    def __pick(self, player):
        if not self.onfield:
            msg = 'カードが盤上にないわ'
        else:
            if self.monsters[self.onfield]['name'] is not None:
                self.players[player].append(self.onfield)
                self.players[player].extend(self.pool)
                self.onfield = None
                self.pool = []
                msg = player + 'が獲得したようね\n'\
                        '今のところ**' + str(len(self.players[player])) + '**ポイントよ'
                if len(self.deck) == 1:
                    msg += 'ちなみに次が最後のカードよ'
            else:
                msg = 'そのカードにはまだ名前が付けられていないわ\n'\
                        '`/name`で素敵な名前を付けてあげて'
        return msg


    def __show_status(self):
        unknown_monsters = [i for i in self.monsters.keys() if self.monsters[i]['name'] is None]
        msg = 'いまのゲーム状況はこんな感じね\n'\
                '山札: **'+ str(len(self.deck)) +'**枚\n'\
                '捨札: **'+ str(len(self.pool)) +'**枚\n'\
                '未発見のモンスター: **'+ str(len(unknown_monsters)) +'**種類\n'
        return msg


    def __show_record(self):
        msg = 'いまの成績はこんな感じね\n'
        for k, v in zip(self.players.keys(), self.players.values()):
            msg += '{name}: {keeps}ポイント\n'.format(name=k, keeps=str(len(v)))
        return msg


    def __show_monster(self, monster):
        img_path = monster['img_path']
        name = '_undefined_' if monster['name'] is None else monster['name']
        return (name, discord.File(img_path))


    def __show_help(self):
        msg = 'コマンド一覧よ\n'\
                '`/join`: マッチメイク時にプレイヤーを登録\n'\
                '`/close`: プレイヤー登録を締切りゲームを開始\n'\
                '`/turn`: 山札からカードを表示\n'\
                '`/name hoge`: 表示されているカードを_hoge_と命名\n'\
                '`/trash`: 表示されているカードを捨札に移動\n'\
                '`/pick`: 表示されているカードを発言プレイヤーの手札に移動\n'\
                '`/status`: 現在の山札と捨札，未発見のカードの枚数を表示\n'\
                '`/record`: 全プレイヤーの名前とポイント(手札枚数)を表示\n'\
                '`/list`: 全カードと名前を表示\n'\
                '`/help`: ヘルプを表示'
        return msg


import re
import random
import json
from glob import glob
from collections import deque

from parse import parse, search
import numpy as np
import discord

from util import shuffle
from cac.daily_accidents import daily_accidents
from cac.daily_items import daily_items


class CachocoMessenger():

    def __init__(self):
        self.gamemode = 'matchmake'

        # players -> {name: {'hand':list of id of item_card in hand, 'scored_accident': list of id of got accident_card}}
        self.players = {}

        self.accident_map = daily_accidents

        self.item_map = daily_items

        self.accidents = deque(shuffle(self.accident_map))
        self.items = deque(shuffle(self.item_map))

        self.onfield_accident = None
        self.onfield_item = []
        self.now_use_item_num = None
        self.item_pool = []
        self.accident_pool = []

    def __call__(self, input_msg, player):
        if self.gamemode == 'matchmake':
            if input_msg.startswith('/join'):
                return self.__register_player(player)
            elif input_msg.startswith('/close'):
                return self.__close_register()
            else:
                return None
        elif self.gamemode == 'ongoing':
            if input_msg.startswith('/turn'):
                return self.__turn_up(player)
            elif input_msg.startswith('/trash'):
                return self.__trash(player)
            elif input_msg.startswith('/pick'):
                return self.__pick(player)
            elif input_msg.startswith('/status'):
                return self.__show_status()
            elif input_msg.startswith('/use'):
                return self.__use_item(input_msg, player)
            elif input_msg.startswith('/record'):
                return self.__show_record()
            return None

    def __str__(self):
        return 'cachoco'

    def __register_player(self, player):
        self.players[player] = {'hand': [], 'scored_accident': []}
        msg = player + 'をプレイヤーとして登録したわ'
        return msg

    def __close_register(self):
        self.gamemode = 'ongoing'
        self.player_order = deque(shuffle(self.players), maxlen=len(self.players))
        self.turn_player = self.player_order[0]

        msg = '登録を締め切ったわ，順番はこんな感じね\n'
        for idx, name in enumerate(self.player_order):
            ordermsg = str(idx+1) + ': ' + name + '\n'
            msg += ordermsg
        msg += '準備できたら手番のプレイヤーは`/turn`と入力するのよ\n'

        deal_item_msg = '\n'.join([self.__deal_items(player) for player in self.player_order])
        msg += deal_item_msg

        return msg

    def __deal_items(self, player):
        deal_num = 3 - len(self.players[player]['hand'])
        msg = '@' + player + 'のアイテムよ\n'
        for i in range(deal_num):
            if not self.items:
                self.items = deque(random.sample(self.item_pool, len(self.item_pool)))
                self.item_pool = []
            picked_item_idx = self.items.popleft()
            self.players[player]['hand'].append(picked_item_idx)
        for idx, item_idx in enumerate(self.players[player]['hand']):
            item_name = self.item_map[item_idx]
            msg += '||' + item_name + '||'
            if idx != 2:
                msg += ', '

        return msg

    def __turn_up(self, player):
        if self.onfield_accident is not None:
            msg = 'すでにカードが盤上にあるわ' 
        elif not self.accidents:
            msg = '山札が無くなっているわ\n'\
                    '次のゲームを始めるのなら`/yasumi cachoco`でリブートして頂戴'
        else:
            msg = "PL: " + player + "\n"
            self.onfield_accident = self.accidents.popleft()
            accident_text = self.accident_map[self.onfield_accident]
            self.now_use_item_num = self.__get_use_item_num() 
            msg += "使うアイテム数: **" + str(self.now_use_item_num) + "個**\n"
            msg += "お題: **" + accident_text + "**"
        return msg

    def __get_use_item_num(self):
        random_num = random.randrange(100)
        if 0 <= random_num and random_num <= 19:
            return 1
        elif 20 <=  random_num and random_num <= 59:
            return 2
        else:
            return 3

    def __trash(self, player):
        if self.onfield_accident is None:
            msg = 'アクシデントカードが盤上にないわ'
        elif len(self.onfield_item) < self.now_use_item_num:
            msg = '十分な数のアイテムカードが使用されていないわ'
        elif self.turn_player != player:
            msg = player + '，今は'+self.turn_player+'のターンよ，あなたじゃない'
        else:
            self.accident_pool.append(self.onfield_accident)
            self.onfield_accident = None
            self.item_pool.extend(self.onfield_item)
            self.onfield_item = []
            self.now_use_item_num = None
            msg = '失敗ね，捨札に移したわ\n'
            deal_item_msg = self.__deal_items(player)
            msg += deal_item_msg + '\n'

            self.player_order.rotate(-1)
            self.turn_player = self.player_order[0]
            msg += '次のプレイヤーは' + self.turn_player + 'よ'
        return msg

    def __pick(self, player):
        if self.onfield_accident is None:
            msg = 'アクシデントカードが盤上にないわ'
        elif len(self.onfield_item) < self.now_use_item_num:
            msg = '十分な数のアイテムカードが使用されていないわ'
        elif self.turn_player != player:
            msg = player + '，今は'+self.turn_player+'のターンよ，あなたじゃない'
        else:
            self.players[player]['scored_accident'].append(self.onfield_accident)
            self.onfield_accident = None
            self.item_pool.extend(self.onfield_item)
            self.onfield_item = []
            self.now_use_item_num = None
            msg = player + 'の成功ね\n'
            deal_item_msg = self.__deal_items(player)
            msg += deal_item_msg + '\n'

            self.player_order.rotate(-1)
            self.turn_player = self.player_order[0]
            msg += '次のプレイヤーは' + self.turn_player + 'よ'
        return msg

    def __use_item(self, input_msg, player):
        if self.onfield_accident is None:
            msg = 'アクシデントカードが盤上にないわ'
        elif len(self.players[player]['hand']) == 0:
            msg = 'もうアイテムカードを持っていないわ'
        elif self.turn_player != player:
            msg = '今は'+self.turn_player+'のターンよ，あなたじゃない'
        else:
            input_item_name, = parse('/use {}', input_msg)
            input_item_idx = [k for k, v in self.item_map.items() if v == input_item_name]
            if len(input_item_idx) == 0:
                msg = 'アイテム名が間違っているようね'
            else:
                input_item_idx = input_item_idx[0]
                if not input_item_idx in self.players[player]['hand']:
                    msg = 'そのアイテムを持っていないようだわ'
                else:
                    self.players[player]['hand'].remove(input_item_idx)
                    self.onfield_item.append(input_item_idx)
                    msg = ''
        return msg

    def __show_status(self):
        msg = 'いまのゲーム状況はこんな感じね\n'\
                'アクシデントカード: '+ str(len(self.accidents)) +'/'+ str(len(self.accident_map)) + ' 枚\n'\
                'アイテムカード: '+ str(len(self.items)) +'/' + str(len(self.item_map)) + ' 枚'
        return msg

    def __show_record(self):
        msg = 'いまの成績はこんな感じね\n'
        for k, v in zip(self.players.keys(), self.players.values()):
            msg += '{name}: {keeps}ポイント\n'.format(name=k, keeps=str(len(v['scored_accident'])))
        return msg

    @classmethod
    def show_help(cls):
        msg = '**yasumi: Cat&Chocolate-commands**\n'\
                '__マッチメイク__\n'\
                '`/join`: 参加するプレイヤーを登録\n'\
                '`/close`: プレイヤー登録を締切りゲームを開始\n'\
                '__メイン__\n'\
                '`/turn`: 山札からアクシデントカードを表示\n'\
                '`/use [item]`: 手札のアイテムカードを使用\n'\
                '`/pick`: 成功したのでアクシデントカードを取得\n'\
                '`/trash`: 失敗したのでアクシデントカードを捨札に移動\n'\
                '`/status`: 現在の山札の枚数を表示\n'\
                '`/record`: 全プレイヤーの名前とポイントを表示'
        return msg


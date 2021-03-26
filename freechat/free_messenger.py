import re

from parse import parse, search
import numpy as np


class FreeChatMessenger():

    def __init__(self):
        pass


    def __call__(self, input_msg, player):
        if input_msg.startswith('/trg'):
            return self.__rolling_girls()
        elif input_msg.startswith('/たばこ'):
            return self.__hate_tobaco()
        else:
            return None


    def __str__(self):
        return 'free'


    def __rolling_girls(self):
        msg = 'Rolling, Falling, Scrambling Girls.\n'
        msg += 'For others. For themselves.\n'
        msg += 'Even if they\'re destined to be a "mob".'
        return msg 


    def __hate_tobacco(self):
        msg = '煙草の煙は主流煙より副流煙の方が有害物質が多く含まれています。\n'
        msg += '発癌性の高いジメチルニトロサミンは主流煙が5.3から43ナノグラムであるのに対して\n'
        msg += '副流煙では680から823ナノグラム。\n'
        msg += 'キノリンの副流煙にいたっては主流煙の11倍、およそ1万8千ナノグラム含まれている。'
        return msg


    @classmethod
    def show_help(cls):
        msg = '**yasumi: Freechat-commands**\n'\
                '`/trg`: The Roling Girls'
        return msg


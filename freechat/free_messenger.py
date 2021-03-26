import re

from parse import parse, search
import numpy as np


class FreeChatMessenger():

    def __init__(self):
        pass


    def __call__(self, input_msg, player):
        if input_msg.startswith('/trg'):
            return self.__rolling_girls()
        else:
            return None


    def __str__(self):
        return 'free'


    def __rolling_girls(self):
        msg = 'Rolling, Falling, Scrambling Girls.\n'
        msg += 'For others. For themselves.\n'
        msg += 'Even if they\'re destined to be a "mob".'
        return msg 


    @classmethod
    def show_help(cls):
        msg = '**yasumi: Freechat-commands**\n'\
                '`/trg`: The Roling Girls'
        return msg


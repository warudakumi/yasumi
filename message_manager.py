from coc.cthulhu_messenger import CthulhuMessenger
from coc.charactors import load_charactors as coc_lc
from nanjamonja.nanja_messenger import NanjaMessenger


class MessageManager():

    def __init__(self, mode, conf):
        if mode == 'coc':
            self.messenger = CthulhuMessenger(coc_lc(conf))
        elif mode == 'nanjamonja':
            self.messenger = NanjaMessenger()
        else:
            raise ValueError('invalid mode value.')


    def switch_cheat(self):
        try:
            self.messenger.switch_cheat()
            if self.messenger.on_cheat:
                return True
            else:
                return False
        except AttributeError:
            raise AttributeError('cannot execute cheat mode.')


    def call(self, input_msg, player):
        return self.messenger.call(input_msg, player)


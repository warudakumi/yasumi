from coc.cthulhu_messenger import CthulhuMessenger


class MessageManager():

    def __init__(self, mode, charactors):
        if mode == 'coc':
            self.messenger = CthulhuMessenger(charactors)
        else:
            raise ValueError("invalid mode value.")

    def call(self, input_msg, player):
        return self.messenger.call(input_msg, player)


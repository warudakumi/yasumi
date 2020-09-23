import sys

import json
import discord
from parse import parse

from message_manager import MessageManager 
from coc.charactors import load_charactors


def main():
    with open ('config.json') as f:
        conf = json.load(f)

    mode = ''
    mm = ''

    client = discord.Client()
    client_id = conf['client_id']

    @client.event
    async def on_ready():
        print('Logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        nonlocal mode
        nonlocal mm 

        if client.user != message.author:
            input_msg = message.content

            if input_msg == '/bye':
                await message.channel.send('[INFO]さようなら！！！！')
                await client.close()
                sys.exit(0)

            elif input_msg.startswith('/yasumi'):
                mode, = parse('/yasumi {}', input_msg).fixed
                charactors = load_charactors(conf)
                try:
                    mm = MessageManager(mode, charactors)
                    await message.channel.send('[INFO]ゲームシステムを**'+mode+'**に設定したわ')
                except ValueError as e:
                    await message.channel.send('[INFO]正しいゲームシステムを入力して頂戴')

            elif input_msg.startswith('/'):
                if not mode:
                    await message.channel.send('[INFO]ゲームシステムが設定されてなくない？')

                else:
                    player = str(message.author)
                    msg = 'PL:' + player + '\n'
                    msg += mm.call(input_msg, player)
                    await message.channel.send(msg)

    client.run(client_id)

if __name__ == '__main__':
    main()


import sys
import time

import json
import discord
from parse import parse

from message_manager import MessageManager 


def main():
    with open ('config.json') as f:
        conf = json.load(f)

    mode = ''
    mm = None
    voice = None

    client_id = conf['client_id']
    sound_file = conf['sound_file']

    client = discord.Client()

    @client.event
    async def on_ready():
        print('Logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        nonlocal mode
        nonlocal mm 
        nonlocal voice
        nonlocal sound_file

        if client.user != message.author:
            input_msg = message.content

            if input_msg == '/bye':
                await message.channel.send('[INFO]ごきげんよう')
                await client.close()
                sys.exit(0)

            elif input_msg == '/sound':
                if not voice:
                    await message.channel.send('[INFO]ゲームシステムが設定されていないようね')
                else:
                    voice.play(discord.FFmpegPCMAudio(sound_file))

            elif input_msg.startswith('/yasumi'):
                mode, = parse('/yasumi {}', input_msg).fixed
                try:
                    mm = MessageManager(mode, conf)
                    channel = message.author.voice.channel
                    voice = await channel.connect()
                    await message.channel.send('[INFO]ゲームシステムを**'+mode+'**に設定したわ')
                except ValueError as ve:
                    await message.channel.send('[INFO]正しいゲームシステムを入力して頂戴')
                except AttributeError as ae:
                    await message.channel.send('[INFO]適当なボイスチャンネルにログインして貰えるかしら')

            elif input_msg.startswith('/'):
                if not mode:
                    await message.channel.send('[INFO]ゲームシステムが設定されていないようね')
                elif mode == 'coc':
                    player = str(message.author)
                    msg = 'PL:' + player + '\n'
                    msg += mm.call(input_msg, player)
                    await message.channel.send(msg)
                elif mode == 'nanjamonja':
                    player = str(message.author)
                    msg = mm.call(input_msg, player)

                    # in case of list command
                    if isinstance(msg, list):
                        for sub_msg in msg:
                            await message.channel.send(sub_msg[0], file=sub_msg[1])
                            time.sleep(1.0)

                    # in case of show image
                    else:
                        if isinstance(msg, tuple):
                            await message.channel.send(msg[0], file=msg[1])
                        else:
                            await message.channel.send(msg)

    client.run(client_id)

if __name__ == '__main__':
    main()


import sys
import time

import json
import discord
from discord import ClientException
from parse import parse

from message_manager import MessageManager 


def main():
    with open ('config.json') as f:
        client_id = json.load(f)['client_id']

    mm = None
    voice = None
    sound_map = {}

    client = discord.Client()

    @client.event
    async def on_ready():
        print('[yasumi]Logged in as {0.user}'.format(client))
    @client.event
    async def on_message(message):
        nonlocal mm 
        nonlocal voice
        nonlocal sound_map

        if client.user != message.author:
            input_msg = message.content

            if input_msg == '/bye':
                await message.channel.send('[INFO]ごきげんよう')
                await client.close()
                sys.exit(0)

            elif input_msg.startswith('/yasumi init'):
                if input_msg == '/yasumi init':
                    mode = 'free'
                else:
                    mode, = parse('/yasumi init {}', input_msg).fixed
                try:
                    with open ('config.json') as f:
                        conf = json.load(f)

                    sound_map = conf['sound']
                    mm = MessageManager(mode, conf)
                    channel = message.author.voice.channel
                    try:
                        voice = await channel.connect()
                    except ClientException:
                        print('[yasumi]Allready connected voice channel, continue.'.format(client))
                        pass

                    await message.channel.send('[INFO]イニシャライズしたわ(システム: **'+mode+'**)')

                except ValueError as ve:
                    await message.channel.send('[INFO]登録されていないシステムよ: __'+mode+'__')
                except AttributeError as ae:
                    await message.channel.send('[INFO]適当なボイスチャンネルにログインして貰えるかしら')

            elif input_msg.startswith('/yasumi help'):
                if mm is None:
                    await message.channel.send('[INFO]イニシャライズして頂戴')
                else:
                    if input_msg == '/yasumi help':
                        help_at = 'main'
                    else:
                        help_at, = parse('/yasumi help {}', input_msg).fixed
                    try:
                        help_msg = mm.help(help_at, sound_map)
                        await message.channel.send(help_msg)
                    except ValueError as ve:
                        await message.channel.send('[INFO]登録されていないシステムよ: __'+help_at+'__')

            elif input_msg.startswith('/'):
                if mm is None:
                    await message.channel.send('[INFO]イニシャライズして頂戴')
                else:
                    player = str(message.author)
                    msg = mm(input_msg, player)

                    if isinstance(msg, str):
                        await message.channel.send(msg)

                    elif isinstance(msg, list):
                        for sub_msg in msg:
                            await message.channel.send(sub_msg[0], file=sub_msg[1])
                            time.sleep(1.0)

                    elif isinstance(msg, tuple):
                        await message.channel.send(msg[0], file=msg[1])

                    else:
                        await message.channel.send('[INFO]無効なコマンドよ: __'+input_msg+'__')


            elif input_msg.startswith('#'):
                if not voice:
                    await message.channel.send('[INFO]イニシャライズして頂戴')
                else:
                    try:
                        voice.play(discord.FFmpegPCMAudio(sound_map[input_msg]))
                    except KeyError:
                        await message.channel.send('[INFO]登録されていないサウンドよ: __'+input_msg+'__')
                    except ClientException:
                        await message.channel.send('[INFO]いま別のを再生しているわ')

    client.run(client_id)


if __name__ == '__main__':
    main()


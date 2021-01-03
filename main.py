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
    mm = ''
    command = ''

    client = discord.Client()
    client_id = conf['client_id']

    @client.event
    async def on_ready():
        print('Logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        nonlocal mode
        nonlocal mm 
        nonlocal command

        if client.user != message.author:
            input_msg = message.content

            # dm only
            if message.author.dm_channel is not None:
                if message.channel.id == message.author.dm_channel.id:
                    if input_msg == '/kick':
                        guild_id = conf['guild_id']
                        channel_id = conf['channel_id']
                        user_id = conf['user_id']

                        guild = client.get_guild(guild_id)
                        channel = client.get_channel(channel_id)
                        user = await client.fetch_user(user_id)
                        # await guild.kick(user)
                        embed = discord.Embed(title='新着メッセージ(1)', color=0xff0000)
                        embed.add_field(name='To:', value=user, inline=False)
                        embed.add_field(name='From:', value='蠢玲･ｽ鮗�', inline=False)
                        embed.add_field(name='Attached:', value='inori_ver2_scanned.png', inline=False)
                        embed.set_image(url='https://i.imgur.com/KIIuOMT.png')
                        embed.add_field(name='Main:', value='繝舌ド峨ン繝は≧縺斐こ｣縺ｦってわけ', inline=False)
                        await channel.send(embed=embed)

                        time.sleep(5.0)
                        await client.close()
                        sys.exit(0)

                    elif input_msg == '/cheat':
                        try:
                            on_cheat = mm.switch_cheat()
                            cheat_msg = 'チートモードね' if on_cheat else '通常モードね' 
                            await message.channel.send(cheat_msg)
                        except AttributeError:
                            await message.channel.send('いまのモードだと使用できないわ')

            # group dm only
            elif not message.guild:
                pass

            # server text channel
            else:
                if input_msg == '/bye':
                    await message.channel.send('[INFO]ごきげんよう')
                    await client.close()
                    sys.exit(0)

                elif input_msg.startswith('/yasumi'):
                    mode, = parse('/yasumi {}', input_msg).fixed
                    try:
                        mm = MessageManager(mode, conf)
                        await message.channel.send('[INFO]ゲームシステムを**'+mode+'**に設定したわ')
                    except ValueError as e:
                        await message.channel.send('[INFO]正しいゲームシステムを入力して頂戴')

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
                        else:
                            # in case of show image
                            if isinstance(msg, tuple):
                                await message.channel.send(msg[0], file=msg[1])
                            else:
                                await message.channel.send(msg)

    client.run(client_id)

if __name__ == '__main__':
    main()


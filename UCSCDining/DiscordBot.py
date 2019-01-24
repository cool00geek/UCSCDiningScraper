#!/usr/bin/env python3

import discord
import os
from UCSCDining import UCSCDining
import DiningBot

token = os.environ.get('DISCORD_UCSC_KEY')

client = discord.Client()



@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    print(str(message.author) + " sent message: " + str(message.content))
    DiningBot.store_from(str(message.author), 'discord_users.txt')

    if message.content.lower().startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    elif message.content.lower().startswith('!start') or message.content.startswith('!help'):
        msg = DiningBot.help(platform="Discord", prefix="!")
        await client.send_message(message.channel, msg)
    elif message.content.lower().startswith('!about'):
        msg = DiningBot.about(platform="Discord")
        await client.send_message(message.channel, msg)
    elif message.content.lower().startswith('!menu'):
        msg = DiningBot.parse(message.content, platform="DC", prefix="!")
        if not msg:
            await client.send_message(message.channel, "I'm not sure what college that is!")
        else:
            await client.send_message(message.channel, msg)
    #elif message.content.startswith('!'):
    #    msg = "I don't understand that command!"
    #    await client.send_message(message.channel, msg)
    elif message.content.lower().startswith('hello there'):
        msg = "General Kenobi"
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)

import os

import discord
from dotenv import load_dotenv


async def process_message(message):
    try:
        await message.channel.send(message.content)
    except Exception as error:
        print(error)

def run_bot():
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print({client.user}, 'is live')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        await process_message(message)

    client.run(bot_token)

import os

import discord
import requests
from dotenv import load_dotenv


def run_bot():
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user.name} is live')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        await get_card_name(message)

    client.run(bot_token)

async def get_card_name(message):
    names = message.content.split('[')[1:]
    if not len(names):
        return
    for name in names:
        closing_bracket = name.find(']')
        if closing_bracket == -1:
            return
        await get_card(message, name[:closing_bracket])

async def get_card(message, card_name):
    try:
        url = f'https://api.scryfall.com/cards/named?fuzzy={card_name}'
        response = requests.get(url)
        if response.status_code == 200:
            await send_response(message, response.json())
            return
        await send_error_response(message, response.json()['details'])
    except Exception as error:
        print(error)

async def send_response(message, card_data):
    scryfall_uri = card_data['scryfall_uri']
    embedded_message = discord.Embed()
    embedded_message.description = f'[Scryfall]({scryfall_uri})'
    if 'image_uris' in card_data:
        await message.channel.send(card_data['image_uris']['border_crop'])
        await message.channel.send(embed=embedded_message)
        return
    front_face = card_data['card_faces'][0]['image_uris']['border_crop']
    back_face = card_data['card_faces'][1]['image_uris']['border_crop']
    await message.channel.send(f'{front_face} {back_face}')
    await message.channel.send(embed=embedded_message)

async def send_error_response(message, error_message):
    await message.channel.send("¯\_(ツ)_/¯\nError Message: {0}".format(error_message))

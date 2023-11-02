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

async def get_card(message, fuzzy_card_name):
    try:
        url = f'https://api.scryfall.com/cards/named?fuzzy={fuzzy_card_name}'
        response = requests.get(url)
        if response.status_code == 200:
            await send_response(message, response.json())
            return
        await send_error_response(message, response.json()['details'])
    except Exception as error:
        print(error)

async def send_response(message, card_data):
    embedded_message = discord.Embed()
    embedded_message.description = get_embedded_links(card_data['scryfall_uri'], card_data['type_line'],
                                                      card_data['legalities'], card_data['name'])
    if 'image_uris' in card_data:
        await message.channel.send(card_data['image_uris']['border_crop'])
        await message.channel.send(embed=embedded_message)
        return
    front_face = card_data['card_faces'][0]['image_uris']['border_crop']
    back_face = card_data['card_faces'][1]['image_uris']['border_crop']
    await message.channel.send(front_face)
    await message.channel.send(back_face)
    await message.channel.send(embed=embedded_message)

def get_embedded_links(scryfall_uri, type_line, legalities, card_name):
    scryfall_link = f'[Scryfall]({scryfall_uri})'
    if not commander_legal(type_line, legalities):
        return scryfall_link
    edh_rec_base_url = 'https://edhrec.com/commanders'
    formatted_name = format_card_name_for_url(card_name)
    edh_rec_link = f'[EDHRec]({edh_rec_base_url}/{formatted_name})'
    return f'{scryfall_link}\t|\t{edh_rec_link}'

def commander_legal(type_line, legalities):
    return 'Legendary Creature' in type_line and legalities['commander'] == 'legal'

def format_card_name_for_url(card_name):
    replace_spaces = card_name.replace(' ', '-')
    return replace_spaces.translate({ord(i): '' for i in ',\''}).lower()

async def send_error_response(message, error_message):
    await message.channel.send('¯\_(ツ)_/¯\n{0}'.format(error_message))

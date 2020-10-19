import os
import discord
from dotenv import load_dotenv

import subprocess
import requests
import json


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def alNumOrComma(s):
    return s == ',' or s.isalnum()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(f'{client.user} has connected!')
    print(f'{guild.name}(id: {guild.id})')

@client.event
async def on_message(message):
    if message.content.startswith('!texor'):
        formatted_message = message.content[6:]
        formatted_message = formatted_message.replace('\\', '\\\\...')

        latex_string = '\\...documentclass[preview, border={1mm 1mm 1mm 0mm}]{standalone}\n\\...usepackage{amsmath}\n\\...usepackage{varwidth}\n\\...usepackage[dvipsnames]{xcolor}\n\\...begin{document}\n\\...begin{varwidth}{\linewidth}\n\\...pagecolor{black}\n\t\\...begin{equation*} \n\t\t' + formatted_message + '\n\t\\...end{equation*}\n\\...end{varwidth}\n\\...end{document}'
        subprocess.run('printf \'\' > latex.tex', shell=True, stdout=subprocess.PIPE)

        for segment in latex_string.split('...'):
            bashCmd=['printf' + ' \'' + segment + '\'' + '>> latex.tex']
            subprocess.run(bashCmd, shell=True, stdout=subprocess.PIPE)
        
        bashCmd=['pdflatex -interaction=nonstopmode latex.tex']
        subprocess.run(bashCmd, shell=True, stdout=subprocess.PIPE)

        bashCmd=['mkdir -p images && pdftoppm -jpeg -r 1200 latex.pdf images/latex']
        subprocess.run(bashCmd, shell=True, stdout=subprocess.PIPE)

        await message.channel.send(file=discord.File('images/latex-1.jpg'))
        
        bashCmd=['rm -f images/latex-1.jpg']
        subprocess.run(bashCmd, shell=True, stdout=subprocess.PIPE)
    elif message.content.startswith('!oeis'):
        formatted_message = message.content[5:]
        formatted_filter = filter(alNumOrComma, formatted_message)
        formatted_message = ''.join(formatted_filter)

        url = 'https://oeis.org/search?fmt=json&q=' + formatted_message + '&start=0'
        oeis_json = json.loads(requests.get(url).text)


        if (oeis_json['count'] == 0):
            await message.channel.send('no sequence was found')
        else:
            await message.channel.send(oeis_json['results'][0]["name"])
            await message.channel.send(oeis_json['results'][0]["data"])
            num_results = min(3, len(oeis_json['results'][0]["formula"]))
            for i in range(num_results):
                await message.channel.send(oeis_json['results'][0]["formula"][i])

client.run(DISCORD_BOT_TOKEN)



exit(0)
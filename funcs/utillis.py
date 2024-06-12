import os, re
import sys, time
import aiohttp
from configparser import ConfigParser
from threading import *
from datetime import datetime
from flask import Flask, render_template
from itertools import cycle
from funcs.planet import run_preview
#from main import log_wk
import random

import disnake
from disnake import TextChannel, Webhook
from disnake.ext import commands,tasks

import requests as req
from discord_webhook import DiscordWebhook

config = ConfigParser()
config.read(r'config.ini')

async def autoscan(message):
    if not message:
        return

    pixelgame = None
    g = None
    canvas = None
    x = None
    y = None
    zoom = None
    diff = None

    m_pc = re.search(r'pixelcanvas\.io/@(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
    m_ppfun = re.search(r'pixelplanet\.fun/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
    m_pix = re.search(r'pixelya\.fun/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
    m_canvas = re.search(r'canvaspixel\.net/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
    
    m_pre_def = re.search(r'@(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
    m_pre_def_ppfun = re.search(r'pixelya\.fun/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)#re.search(r'#(-?\w+),(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)

    
    if m_canvas:
        pixelgame = 'canvaspixel'
        g = m_canvas.groups()

    elif m_pre_def and len(message.attachments) > 0 and message.attachments[0].filename[-4:].lower() == ".png":
        pixelgame = 'pixelcanvas'
        diff = message.attachments[0]
        g = m_pre_def.groups()
    elif m_pre_def_ppfun and len(message.attachments) > 0 and message.attachments[0].filename[-4:].lower() == ".png":
        pixelgame = 'pixelya'
        diff = message.attachments[0]
        g = m_pre_def_ppfun.groups()
    elif m_pix:
        pixelgame = 'pixelya'
        g = m_pix.groups()
    elif m_pre_def:
        pixelgame = 'pixelcanvas'
        g = m_pre_def.groups()
    elif m_pre_def_ppfun:
        pixelgame = 'pixelplanet'
        g = m_pre_def_ppfun.groups()
    elif m_pc:
        pixelgame = 'pixelcanvas'
        g = m_pc.groups()
    elif m_ppfun:
        pixelgame = 'pixelplanet'
        g = m_ppfun.groups()

    #print(pixelgame, g, diff)

    if pixelgame:
        if len(g) == 4:
            canvas = g[0]
            x = g[1]
            y = g[2]
            zoom = g[3] if g[3] != None else 1
        else:
            canvas = None
            x = g[0]
            y = g[1]
            zoom = g[2] if g[2] != None else 1

        await run_preview.compareImg(message, pixelgame, canvas, x, y, zoom, diff)
        return True
    else:
      return False

async def print_welcome_message(guild):
    #yes this is straight from starlight glimmer
    """Print a welcome message when joining a new server."""
    channels = (x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel)
    c = next((x for x in channels if x.name == "general"), next(channels, None))
    newpath = f'./factions/{guild.id}' 
    prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{guild.id}")]
  
    if c:
        await c.send("I'm {0}. If you need any help: ***dsc.gg/brasilop*** or ***@Ev3rTon***. \n "
                     "Supporting only PixelPlanet.fun, Canvaspixel.net, pixelya.fun, Pixelcanvas.io. \nHosted on free service".format('Phi brother'))
        if len(prefixed) == 0:
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                #shutil.copy('_phi_-418_-21_e_.png', newpath)
                #await c.send("👍 Use /setup (name), Creates a faction (needed to use the bot)")
            else:
                await c.send("> Looks like you've already setup your faction! If it's still not working, notify ***dsc.gg/brasilop*** or ***@Ev3rTon***.")
        else:
            await c.send(f"> This server already has a faction named {[filename for filename in os.listdir('./factions/') if filename.startswith(f'{guild.id}')][0]} \n> To change your faction's name use /setupchange (name)")
        
        print("[CONSOLE] Printed welcome message")
    else:
        print("[CONSOLE] Could not print welcome message: no default channel found")
      

wh_log = config['BOTCONFIG']['log']#
async def log_wk(msg):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(wh_log, session=session)
        await webhook.send(f'{msg}', username='Porra')


async def voidping():
    r = {}
    r_s = 0
    now = datetime.now()
    ping = '<@&997263386872139917>'
    ping2 = '<@&1118594570893148236>'
    ping3 = '<@&1180224195284709506>'
    #wh = f'https://discord.com/api/webhooks/1071927421663707196/VDCtFkJY0JRk1uQiBq1PkTUuLPgnBqiKMjfe6ejZZbLoFVQvNHQe0reyl3b05o8V_IPu' # Porra
    wh_log = 'https://discord.com/api/webhooks/996830405263114331/JKAp3G6_fyu_sxf6-5wY5MiGmiedyaFJ98ZH0gg921DVDJQCmEB3Ka6xGPnQoNRw3EbN'

    wh = 'https://discord.com/api/webhooks/1072337528083976343/jqT1CcWBRPsGdCstM-i6pvQvzcDn-guRWXZ3w5VBWYdV4lCC_vaPe1WplhxJuN1Q9mq1'
    wh2 = 'https://discord.com/api/webhooks/1119239972524929085/jUOooMXZugytfMlsFbv5vaNs7j0Nxv8rz0wae470dkNGveVLxzARh1cYPWem0u6k60Ch'

    wh3 = 'https://discord.com/api/webhooks/1180324356128243733/IhTt9ALSKFoboEyDao-zpFPpAv1Dq4HS9TPl-28RdmqEVyTk_v8nAE2DOuX6hqKm5wta'

    header = {
      "user-agent":
      "Mozilla/5.0 (Linux; Android 11; M2003J15SC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36",
      "authority": "pixelplanet.fun",
      "accept": "*/*",
      "accept-language": "en-US,en;q=0.9"
    }

    ultimo = 0
    while True:
        r = req.get('https://pixelplanet.fun/api/chathistory?cid=1&limit=30',
                headers=header)
        r_s = r.status_code
        if r.status_code == 200:
            print(r.status_code)
            r = r.text
      #r =  r.replace('/\[|]|,|"/g', '')
            nome = 'event'
            if nome in r:
                print("tem")
                win = 'Threat successfully defeated. Good work!'
                nao = 'Threat couldn'
                f = 'Celebration time over'
        #slep = 28 * 60
                if f in r:
                    ultimo = 1
                    webhook = DiscordWebhook(url=f'{wh}',
                                   content='O efeito do void acabou.')
                    webhook2 = DiscordWebhook(url=f'{wh2}',
                                    content='Se ha acabado el efecto.')
                    webhook3 = DiscordWebhook(url=f'{wh3}',
             content='The void effect is over.')
                    response = webhook.execute()
                    time.sleep(10)
                    response2 = webhook2.execute()
                    time.sleep(10)
                    response3 = webhook3.execute()
                    print('F 2s')
                    slep = 60 * 60
                    time.sleep(slep)
                elif win in r:
                    ultimo = 2
                    webhook = DiscordWebhook(url=f'{wh}',
                                   content=f'Void ganho, 2/4s {ping}')
                    webhook2 = DiscordWebhook(
                        url=f'{wh2}', content=f'Se ha ganado el void 2/4s {ping2}')
                    webhook3 = DiscordWebhook(
                        url=f'{wh3}', content=f'Void defended 2/4s {ping3}')
                    response = webhook.execute()
                    time.sleep(10)
                    response2 = webhook2.execute()
                    time.sleep(10)
                    response3 = webhook3.execute()
                    
                    print('good')
                    slep = 29 * 60
                    time.sleep(slep)
                elif nao in r:
                    ultimo = 3
                    webhook = DiscordWebhook(url=f'{wh}', content='Perderam o void! :(')
                    webhook2 = DiscordWebhook(url=f'{wh2}',
                                    content='Se ha perdido el void')
                    webhook = DiscordWebhook(url=f'{wh3}', content='Lost the void! :(')
                    response = webhook.execute()
                    time.sleep(10)
                    response2 = webhook2.execute()
                    time.sleep(10)
                    response3 = webhook3.execute()
                    
                    print('perderam')
                    slep = 60 * 60
                    time.sleep(slep)
        else:
            ultimo = 0
            print('Error:', r.status_code)
            webhook = DiscordWebhook(url=f'{wh_log}',
                               content=f'Error: {r.status_code}')
            response = webhook.execute()

        if r.status_code == 403:
            time.sleep(1)
        #system("busybox reboot")
            z = random.randint(30, 40)
            time.sleep(z)
    #break

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

from configparser import ConfigParser
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
      

wh_log = config['BOTCONFIG']['log']#os.environ['wh_log']
async def log_wk(msg):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(wh_log, session=session)
        await webhook.send(f'{msg}', username='Porra')

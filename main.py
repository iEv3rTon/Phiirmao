import os, re
import sys, time
import typing
import aiohttp
from configparser import ConfigParser
from threading import *
from datetime import datetime
from flask import Flask, render_template
from itertools import cycle
import random

import disnake
from disnake import TextChannel, Webhook
from disnake.ext import commands,tasks
from funcs.utillis import print_welcome_message, autoscan, log_wk, voidping

#merda ipnicial
print(f"[CONSOLE] Starting.")
print(f"[CONSOLE] List of factions: {os.listdir('factions/')}.")
#configuraçoes
config = ConfigParser()
config.read(r'config.ini')

try:
    bot_name = config['BOTCONFIG']['name']
    token = os.environ['TOKEN'] #config['BOTCONFIG']['token'] #os.environ['TOKEN']#
    auth_id = config['BOTCONFIG']['auth_id']
    prefix = config['BOTCONFIG']['prefix']
except:
    print('Error parsing config file')
    exit()

#config do bote
#disnake presence. se o bot for banido por causa de erros, mudar isso pra uma task async

now = datetime.now()
app = Flask(__name__)
#
# flask App
#
@app.route('/')
def hello():
  return render_template('index.html',
                         now=now, now2=datetime.now())    
def run():
  app.run(host='0.0.0.0', port=8080)

##
class MyClient(disnake.ext.commands.Bot):
    def get_ratelimit(self, message: disnake.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def on_ready(self):
        self.change_status.start()
        self._cd = commands.CooldownMapping.from_cooldown(1, 4.0, commands.BucketType.guild) # Change accordingly
                                                        # rate, per, BucketType
        print('-'*10)
        print(f'[CONSOLE] Bot started as {self.user}. ID: {self.user.id}. Latency: {self.latency}. Prefix: "{prefix}"')
        print('-'*10)
        #await self.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f'-> Porra <-'))
      
    status = cycle(['-> Porra <-', 'pixelplanet.fun', 'pixelya.fun', 'pixelcanvas.io', 'Faz o L', 'PauPika.fun', '777'])
    n = random.randint(8,50)
    @tasks.loop(seconds=random.randint(8,50))
    async def change_status(self):
      global now2
      
      now2=datetime.now()
      c = self.get_channel(1137551755744399471)
      await c.send(f"change {now2-now}")
      print('change ', now2-now)
      
      await self.change_presence(status=disnake.Status.online, activity=disnake.Game(next(self.status)))
      #await bot.change_presence(activity=discord.Game(next(status)))
  
        #await self.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f"We're back: -GIVE THE BOT 'Application commands' permissions. TYPE /setup (faction_name) BEFORE USING THE BOT"))
    
    async def on_message(self, message):
        # if message.content.startswith("g!"):
        #    await message.add_reaction('🤔')
        # if ' phi ' in message.content.lower() or ' phi' in message.content.lower() or 'phi ' in message.content.lower() or 'phi' == message.content.lower():
        #    await message.add_reaction('🤔')
        
        # Ignore channels that can't be posted in
        if message.guild and not message.channel.permissions_for(message.guild.me).send_messages:
            return

        # Ignore other bots
        if message.author.bot:
            return
        
        # Ignore messages with spoilered images
        for attachment in message.attachments:
            if attachment.is_spoiler():
                return

        # Ignore messages with any spoilered text
        if re.match(r".*\|\|.*\|\|.*", message.content):
            return
        m_pc = re.search(r'pixelcanvas\.io/@(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
        m_ppfun = re.search(r'pixelplanet\.fun/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
        m_pix = re.search(r'pixelya\.fun/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
        m_canvas = re.search(r'canvaspixel\.net/#(-?\w+),(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)

        m_pre_def = re.search(r'@(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)
        m_pre_def_ppfun = re.search(r'#(-?\w+),(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', message.content)

        if m_pc or m_ppfun or m_pre_def or m_pre_def_ppfun or m_pix or m_canvas:
          if "check something":
              # Getting the ratelimit left
              ratelimit = self.get_ratelimit(message)
              if ratelimit is None:
                  # The user is not ratelimited, you can add the XP or level up the user here
                  # Autoscan, since the message contained no command
                  await autoscan(message)
              else:
                  # The user is ratelimited
                  print('limite')
  
    async def on_guild_remove(self, guild):
        print("[CONSOLE] Kicked from guild '{0.name}' (ID: {0.id})".format(guild))
        msg = "[CONSOLE] Kicked from guild '{0.name}' (ID: {0.id})".format(guild)
        await log_wk(msg)

    async def on_guild_join(self, guild):
        #Configuração inicial pra cada server. Neccessário que rodem o comando de configuração
        print(f"[CONSOLE] Joined new guild '{guild.name}' (ID: {guild.id})")
        msg = f"[CONSOLE] Joined new guild '{guild.name}' (ID: {guild.id})"
        await log_wk(msg)
        await print_welcome_message(guild)

intents = disnake.Intents.default()
intents.members = False
intents.message_content = True
client = MyClient(command_prefix=prefix,intents=intents)

initial_extensions = [("cogs." + filename[:-3]) for filename in os.listdir('./cogs')]
for extension in initial_extensions:
    if extension.startswith('cogs.__pycach'):
        pass
    else:
        #client.load_extension(extension)
      try:
        client.load_extension(extension)
      except Exception as e:
        print(e)
        #log_wk(e)

print('[CONSOLE] All cogs loaded.')

if __name__ == '__main__':
  t = Thread(target=run)
  t.start()
  t2 = Thread(target=voidping)
  t2.start()

  while True:
    try:
      client.run(token)
    except Exception as e:
      print(e)
      #log_wk(e)
      time.sleep(15)
      #sys("kill 1")
      time.sleep(15)
  

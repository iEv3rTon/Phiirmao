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
from funcs.utillis import print_welcome_message, autoscan, log_wk
import asyncio
import requests as req
from funcs.planet import pixelya_funcs 

#merda ipnicial
print(f"[CONSOLE] Starting.")
print(f"[CONSOLE] List of factions: {os.listdir('factions/')}.")
#configuraçoes
config = ConfigParser()
config.read(r'config.ini')

try:
    bot_name = config['BOTCONFIG']['name']
    token = config['BOTCONFIG']['token'] #os.environ['TOKEN']#
    auth_id = config['BOTCONFIG']['auth_id']
    prefix = config['BOTCONFIG']['prefix']
    channel_id = config['BOTCONFIG']['channel_id']
    msg_id = config['BOTCONFIG']['msg_id']
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
# Discord
#
class MyClient(disnake.ext.commands.Bot):
    def get_ratelimit(self, message: disnake.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def on_ready(self):
        self.change_status.start()
        self.ranking.start()
        self._cd = commands.CooldownMapping.from_cooldown(1, 4.0, commands.BucketType.guild) # Change accordingly
                                                        # rate, per, BucketType
        print('-'*10)
        print(f'[CONSOLE] Bot started as {self.user}. ID: {self.user.id}. Latency: {self.latency}. Prefix: "{prefix}"')
        print('-'*10)
        #await self.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f'-> Porra <-'))
      
    status = cycle(['-> Porra <-', 'Pixelya.fun', 'Faz o L', 'PauPika.fun'])
    
    n = random.randint(8,50)
    @tasks.loop(seconds=random.randint(8,50))
    async def change_status(self):
      global now2
      
      now2=datetime.now()
      c = self.get_channel(1137551755744399471)
      #await c.send(f"change {now2-now}")
      #print('change ', now2-now)
      
      await self.change_presence(status=disnake.Status.online, activity=disnake.Game(next(self.status)))
      
    #
    # Faction Ranking update
    #
    @tasks.loop(hours=1)
    async def ranking(self):            
      leaderboard_data = await pixelya_funcs.get_fac_ranking()
      if not leaderboard_data:
        return

      embed = disnake.Embed(color=disnake.Color.green())
      embed.set_author(
              name="Faction ranking.",
              icon_url="https://th.bing.com/th/id/OIP.ymxXwyC3fRnfW7O91qgHogHaHa?rs=1&pid=ImgDetMain"
              )

      # limit the leaderboard to 10 entries
      count = 0
      for index in range(len(leaderboard_data)):
          name = leaderboard_data[count]['name']
          tag = leaderboard_data[count]['tag']
          totalpixels = leaderboard_data[count]['tp']
          dailypixels = leaderboard_data[count]['dp']
          players = leaderboard_data[count]['mp']
          avatar = leaderboard_data[count]['avatar']

          embed.add_field(name=f"#{index+1} - [{tag}] {name}", value=f'Members: **{players}** \nTotalPixels: **{totalpixels}**px | DailyPixels: **{dailypixels}**px', inline=False)
          count += 1

          # if count == 10:
          #     break

      #embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/BYZJwN1CPUdSJF3KFP6kSssnjiOaJ0Td_UwQXZvH5C8/https/images-ext-2.discordapp.net/external/sNjIAwbxw2asnXqEYIjQDo19FgNfJjTxn9WpnUEFWbI/https/cdn.discordapp.com/icons/964967008062021682/8a5a72cffd52ea5014587daa9d338731")
      embed.set_footer(text=f'Automatically updates hourly. Last: {datetime.now()}')
      
      channel = self.get_channel(int(channel_id))

      #msg_id = int(msg_id)
      #msg = await channel.fetch_message(msg_id)
      #await msg.edit(embed=embed)

      await channel.send(embed=embed)
      #await ctx.reply(embed=embed, mention_author=False)


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

  while True:
    try:
      client.run(token)
    except Exception as e:
      print(e)
      #log_wk(e)

  

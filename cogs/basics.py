import os
from xmlrpc import client

import disnake
from disnake.ext import commands
from disnake.ext.commands import Command, HelpCommand
import shutil


class Basics(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(description='Answers the bot\'s invite to be shared')
    async def invite(self, inter: disnake.ApplicationCommandInteraction):
        try:
            await inter.response.send_message('Invite PHI with https://discord.com/api/oauth2/authorize?client_id=944655646157066280&permissions=0&scope=bot',) #file=disnake.File('giphy.gif'))
        except Exception as e:
            print(e)
    #@invite.autocomplete("template")
    #async def template_autocomp(self, inter: disnake.ApplicationCommandInteraction, string: str):
    #    LANGUAGES = [f"{inter.guild.id}", f"{inter.guild.name}","typescript", "java", "rust", "lisp", "elixir"]
    #    string = string.lower()
    #    return [lang for lang in LANGUAGES if string in lang.lower()]

    @commands.slash_command(description="Information about the bot.")
    async def help(self, inter: disnake.ApplicationCommandInteraction):

        embed = disnake.Embed(
            title=f"Help",
            description=f"Created by @nisanno (update by @Ev3rTon) :) ***F phi***",
            color=0x00FF00,
        )
        # embed.set_author(
        #     name="erros pixels",
        #     url="https://www.google.com.br/",
        #     icon_url="https://pixelya.fun/PixelyaLOGO.png",
        # )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"
        )
        embed.add_field(
                    name="Games suport", value="PixelPlanet.fun \nCanvasPixel.net \npixelya.fun \nPixelcanvas.io", inline=False
                )
        embed.add_field(
                            name="Canvas list", value=f"'e':earth \n'1':1bit \n'm':moon \n't':top10", inline=False
                        )
        embed.add_field(
                            name="Use /setup (name)", value=f"Creates a faction (needed to use the bot).", inline=False
                        )
        embed.add_field(
                            name="Use /add", value=f"fill in the required fields to add your template.", inline=False
                        )
        embed.add_field(
                            name="Github", value=f"https://github.com/insanocs/ArchimedesProject.git", inline=False
                        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Creates a faction (needed to use the bot)")
    async def setup(self, inter: disnake.ApplicationCommandInteraction, name: str):
        if '_' in name:
            await inter.response.send_message("Sorry you can't use underline (_) in your faction name.")
        else:
            newpath = f'./factions/{inter.guild.id}_{name}' 
            prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
            if len(prefixed) == 0:
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                    #shutil.copy('_phi_-418_-21_e_pixelplanet_.png', newpath)
                    await inter.response.send_message("👍 You can use the bot now!")
                else:
                    await inter.response.send_message("Looks like you've already setup your faction! If it's still not working, notify ***dsc.gg/brasilop*** or ***@Ev3rTon***.")
            else:
                await inter.response.send_message(f"This server already has a faction named {[filename for filename in os.listdir('./factions/') if filename.startswith(f'{inter.guild.id}')][0]} \nTo change your faction's name use /setupchange")
    @commands.slash_command(description="Changes your faction name")
    async def setupchange(self, inter: disnake.ApplicationCommandInteraction, name: str):
        if '_' in name:
            await inter.response.send_message("Sorry you can't use underline (_) in your faction name.")
        else:
            print('started it.')
            prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
            print(f'PREFIXED: {prefixed}')
            os.rename(f'./factions/{prefixed[0]}',f'./factions/{inter.guild.id}_{name}')
            await inter.response.send_message(f'Faction name changed to {name} succesfully')
def setup(client):
    client.add_cog(Basics(client))

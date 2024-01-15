import asyncio
import json
import os, sys
import time
from io import BytesIO

import disnake
import matplotlib.pyplot as plt
import requests
from disnake.ext import commands
from funcs import chunk, dataBase, template
from funcs.planet import PlanetHistory
from PIL import Image, ImageChops
from funcs.buttons.diffButton import DiffButton
from funcs.buttons.updateButton import UpdateButton
from funcs.utillis import log_wk

class Diff(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_slash_command_error")
    async def error_handler(self, interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"You have to wait {error.retry_after:.1f} seconds before using that command again."
            )
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(
                f"Only admins of a server can remove the template. And you don't seem to be one. (no ban_members permissions)",
                file=disnake.File("./media/noperms.gif"),
            )

    @commands.cooldown(1, 5)
    @commands.slash_command(name='add',description='Adds a template to your faction.')
    async def add(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str,
        canvas: str,
        x: int,
        y: int,
        image_link: str,
        pixelgame: str,
    ):
        canvasList = ["earth", "1bot", "moon", "top10"]
        pixelyaList = ["world", "graffity", "football"]
        if canvas == "earth":
            canvasCode = "e"
        elif canvas == "1bot":
            canvasCode = "1"
        elif canvas == "moon":
            canvasCode = "m"
        elif canvas == "top10":
            canvasCode = "t"
        #
        # pixelya
        #
        elif canvas == "world":
          canvasCode = "w"
        elif canvas == "graffity":
          canvasCode = "g"
        elif canvas == "football":
          canvasCode = "f"
          
        print(f"[CONSOLE] New template being added from: {inter.guild.name}")
        # Checar se o comando tá certo
        if "_" in name:
            await inter.response.send_message(
                f"Sorry. You can't use _(underline) in your template name."
            )
            print(
                '[ERROR] User added template name with "_"(underline). Stopping operation'
            )

        if canvas in canvasList and pixelgame == "pixelya":
          await inter.response.send_message(
              f"Canvas *{canvas}* does not exist in *{pixelgame}*."
          )
          
        # Checar se o comando tem um canvas existente
        else:
            if canvas in canvasList:
                try:
                    # Checar se o comando tem x e y válidos
                    print(f"x:{x},y:{y}")
                    x = int(x)
                    y = int(y)
                    print(f"x:{type(x)},y:{type(y)}")

                    if pixelgame != "pixelcanvasio":
                        if canvas != "top10":
                            if abs(x) >> 32768 or abs(y) >> 32768:
                                await inter.response.send_message(
                                    f"Coordinates can't be higher than 32768 or lower than -32768"
                                )
                                return
                        else:
                            if abs(x) >> 2048 or abs(y) >> 2048:
                                await inter.response.send_message(
                                    f"Coordinates can't be higher than 2048 or lower than -2048"
                                )
                                return
                    try:
                        # checar modo da url
                        url = image_link
                        print(f"[CONSOLE] Found url: {url}")
                        response = requests.get(url, stream=True)
                        img = Image.open(BytesIO(response.content)).convert("RGBA")
                        saveResult = template.saveTemplate(
                            name, img, [str(x), str(y)], canvasCode, inter.guild.id, pixelgame
                        )
                        if saveResult == 0:
                            await inter.response.send_message(
                                "Seems like your faction still need a setup. Use /setup (name)"
                            )
                        elif saveResult == 1:
                            await inter.response.send_message(
                                "Another template has already been created with that name."
                            )
                        elif saveResult == 2:
                            await inter.response.send_message(
                                f"Template successfully created as {name}"
                            )
                            print(
                                f"Template created as {name} for {inter.guild.id}"
                            )
                            await log_wk(f"Template created as {name} for {inter.guild.id}")
                    except IndexError as e:
                        await inter.response.send_message(
                            f"Sorry I couldn't find your image. Try attaching it to a discord message and linking it on the command.'"
                        )

                except Exception as e:
                    await inter.response.send_message(
                        f"Something seems to have gone wrong. Is your X and Y numbers?"
                    )
                    print(f"[ERROR] X and Y arguments must be numbers. {e}")
                    return

            elif canvas in pixelyaList:
              try:
                # Checar se o comando tem x e y válidos
                print(f"x:{x},y:{y}")
                x = int(x)
                y = int(y)
                print(f"x:{type(x)},y:{type(y)}")

                if pixelgame != "pixelcanvasio":
                    #if canvas != "top10":
                        if abs(x) >> 16768 or abs(y) >> 16768:
                            await inter.response.send_message(
                                f"Coordinates can't be higher than 16768 or lower than -16768"
                            )
                            return
                    #else:
                        # if abs(x) >> 2048 or abs(y) >> 2048:
                        #     await inter.response.send_message(
                        #         f"Coordinates can't be higher than 2048 or lower than -2048"
                        #     )
                        #     return
                try:
                    # checar modo da url
                    url = image_link
                    print(f"[CONSOLE] Found url: {url}")
                    response = requests.get(url, stream=True)
                    img = Image.open(BytesIO(response.content)).convert("RGBA")
                    saveResult = template.saveTemplate(
                        name, img, [str(x), str(y)], canvasCode, inter.guild.id, pixelgame
                    )
                    if saveResult == 0:
                        await inter.response.send_message(
                            "Seems like your faction still need a setup. Use /setup (name)"
                        )
                    elif saveResult == 1:
                        await inter.response.send_message(
                            "Another template has already been created with that name."
                        )
                    elif saveResult == 2:
                        await inter.response.send_message(
                            f"Template successfully created as {name}"
                        )
                        print(
                            f"Template created as {name} for {inter.guild.id}"
                        )
                        await log_wk(f"Template created as {name} for {inter.guild.id}")
                except IndexError as e:
                    await inter.response.send_message(
                        f"Sorry I couldn't find your image. Try attaching it to a discord message and linking it on the command.'"
                    )

              except Exception as e:
                await inter.response.send_message(
                    f"Something seems to have gone wrong. Is your X and Y numbers?"
                )
                print(f"[ERROR] X and Y arguments must be numbers. {e}")
                return
            
            else:
                await inter.response.send_message(
                    f"Unsupported canvas OR wrong usage of command. Type p!canvaslist or or p!help for more info."
                )

    #@commands.cooldown(1, 5)
    #@commands.slash_command(description='Updates your template. Needs admin perms.')
    #@commands.has_permissions(ban_members=True, kick_members=True)
    #async def update(self, inter: disnake.ApplicationCommandInteraction, name: str):
    #    userid = inter.guild.id
    #    username = inter.user.name
    #    print(f"[CONSOLE] Starting Update command for {username}: {name}")
    #    view = UpdateButton()
    #    await inter.response.send_message(f'What would you like to change in ***{name}*** template?', view=view)

    @commands.cooldown(1, 5)
    @commands.slash_command(description='Removes a template from your faction. Needs admin perms in the server.')
    @commands.has_permissions(ban_members=True, kick_members=True)
    async def remove(self, inter: disnake.ApplicationCommandInteraction, name: str):
        userid = inter.guild.id
        username = inter.user.name
        print(f"[CONSOLE] Started Remove command for {username}: {name}")
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templateArr = [
            temp.split("_")
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png") and temp.split("_")[1].startswith(f"{name}")
        ]
        if len(templateArr[0]) == 6:
            _n, tempName, x, y, canvas, fileFormat = templateArr[0]
            pixelgame = 'pixelplanet'
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}"
        else:
            _n, tempName, x, y, canvas, pixelgame, fileFormat = templateArr[0]
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{pixelgame}_{fileFormat}"
        #print(f'comparing: {templateArr[0]}')
        print(f'[CONSOLE] Deleting template {tempName}.')
        await log_wk(f'[CONSOLE] Deleting template {tempName}.')
        os.remove(filename)
        await inter.response.send_message(f'Template ***{tempName}*** is no more. Its configs were: \n***X***: {x}, ***Y***: {y} \n***Game***: {pixelgame}', ephemeral=False)

    @commands.cooldown(1, 15)
    @commands.slash_command(description='See statistics about your template in Pixelgame.')
    async def diff(self, inter: disnake.ApplicationCommandInteraction, name: str):
        userid = inter.guild.id
        username = inter.user.name

        print(f"[CONSOLE] Started Diff command for {username}: {name}")
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templateArr = [
            temp.split("_")
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png") and temp.split("_")[1] == name
        ]

        if len(templateArr[0]) == 6:
            _n, tempName, x, y, canvas, fileFormat = templateArr[0]
            pixelgame = 'pixelplanet'
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}"
        else:
            _n, tempName, x, y, canvas, pixelgame, fileFormat = templateArr[0]
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{pixelgame}_{fileFormat}"
        print(f'comparing: {templateArr[0]}')
        await log_wk(f'comparing: {templateArr[0]}, {username}')
        try:
            tot, err, elapsed = await chunk.ImageManipulation.compareImg(
                inter,
                [int(x), int(y)],
                canvas,
                filename,
                tempName,
                "diff",
                pixelgame
            )
        except Exception as e:
            print(e, sys.exc_info()[2].tb_lineno)

        if canvas == "e":
            canvasCode = 0
            canvasName = "earth"
            canvasLink = "d"
        elif canvas == "1":
            canvasCode = 7
            canvasName = "1bot"
            canvasLink = "w"
        elif canvas == "m":
            canvasCode = 1
            canvasName = "moon"
            canvasLink = "m"
        elif canvas == "t":
            canvasCode = 8
            canvasName = "top10"
            canvasLink = "t"
        #pixelya
        elif canvas == "w":
          canvasCode = 0
          canvasName = "worldmap"
          canvasLink = "w"
        elif canvas == "g":
          canvasCode = 1
          canvasName = "graffity"
          canvasLink = "g"
        elif canvas == "f":
          canvasCode = 2
          canvasName = "football"
          canvasLink = "f"

        dataBase.writeNewNumeric(inter.guild.id, tempName, time.time(), (tot - err)) 
        print(f"[CONSOLE] Unpacking .csv data")
        processed_data = dataBase.readNumericData(inter.guild.id, tempName)

        pixel_rate = (processed_data[-2] - processed_data[-4]) / (
            (processed_data[-1] - processed_data[-3]) / 60 / 60
        )

        if round(pixel_rate) == 0:
            expected_time = f"This is not going anywhere. 0 px/h"
        if pixel_rate > 0:
            expected_time = f'{(tot/pixel_rate) if (tot/pixel_rate) < 36 else (tot/pixel_rate/24):.2f} {"hours" if (tot/pixel_rate) < 36 else "days"} to completion.'
        if pixel_rate < 0:
            expected_time = f'{(tot/pixel_rate) if abs(tot/pixel_rate) < 36 else (tot/pixel_rate/24):.2f} {"hours" if abs(tot/pixel_rate) < 36 else "days"} to destruction. (ouch!)'

        xx = []
        diffs = 0
        for i in range(0, 32):
            if (i % 2) != 0:  # SE É IMPAR
                if processed_data[i] == 0:
                    pass
                else:
                    xx.append((processed_data[32 - 1] - processed_data[i]) / 60 / 60)
                    diffs = diffs + 1
            else:
                pass
        yy = []
        for i in range(0, len(processed_data)):
            if (i % 2) == 0:
                if processed_data[i + 1] == 0:
                    pass
                else:
                    yy.append(100 * processed_data[i] / tot)
            else:
                pass
        print(xx, yy)
        print(plt.style.available)
        with plt.style.context("bmh"):
            print('plotting')
            plt.plot(xx, yy, "g-o")
            plt.fill_between(xx, yy, color='#30b61a', alpha=.2)
            plt.title(f"{tempName} percentage in the last {diffs} diffs")
            plt.xlim(max(xx), min(xx))
            plt.ylim(0, max(yy)+5)
            plt.ylabel("Percentage")
            plt.xlabel("Hours since this diff")
            plt.savefig("./generated/plot.png")
            plt.close()
        print("plot closed")

        if pixelgame != "pixelcanvasio":
            if pixelgame == "pixelplanet":
                gamelink = f"https://www.pixelplanet.fun/#{canvasLink},{x},{y},10"
            elif pixelgame == "canvaspixel":
                gamelink = f"https://www.canvaspixel.net/#{canvasLink},{x},{y},10"
            elif pixelgame == "pixelya":
                gamelink = f"https://pixelya.fun/#{canvasLink},{x},{y},10"
            else:
                gamelink = f"https://www.pixelplanet.fun/#{canvasLink},{x},{y},10"
        else:
            gamelink = f"https://pixelcanvas.io/@{x},{y},0"

        embed = disnake.Embed(
            title="Teleport to coordinates",
            url=gamelink,
            description=f"This took the bot {elapsed:.1f} seconds",
            color=0x00FF00,
        )
        embed.set_author(
            name=f"{pixelgame} Template progress",
            url="https://www.google.com.br/",
            icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"
        )
        embed.add_field(
            name="Placed / Needed",
            value=f"{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)",
            inline=True,
        )
        embed.add_field(
            name="From last",
            value=f"{'+' if (processed_data[-2]-processed_data[-4]) > 0 else ''}{processed_data[-2]-processed_data[-4]}",
            inline=True,
        )
        embed.add_field(
            name="Errors",
            value=f"{err:,}",
            inline=False,
        )
        embed.add_field(
            name="Pixel rate",
            value=f"{f'{round(pixel_rate)} px/h' if processed_data[-4] != 0 else 'NaN px/h'}",
            inline=False,
        )
        embed.add_field(
            name="Expected time at this rate", value=f"{expected_time}", inline=True
        )
        embed.set_footer(
            text=f"Last time this template was diffed: {time.ctime(processed_data[-3])}"
        )
        embed.set_image(file=disnake.File("./generated/difference.png"))
        view = DiffButton(f"https://www.pixelplanet.fun/#{canvasLink},{x},{y},10", filename, x, y, canvas, pixelgame)
        await inter.edit_original_message("Done!",embed=embed, view=view)
        await inter.wait()

    @commands.cooldown(1, 15)
    @commands.slash_command(description='See erros pixels in the template that you wish.')
    async def erros(self, inter: disnake.ApplicationCommandInteraction, name: str):
        userid = inter.guild.id
        username = inter.user.name
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templateArr = [
            temp.split("_")
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png") and temp.split("_")[1].startswith(f"{name}")
        ]
        if len(templateArr[0]) == 6:
            _n, tempName, x, y, canvas, fileFormat = templateArr[0]
            pixelgame = 'pixelplanet'
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}"
        else:
            _n, tempName, x, y, canvas, pixelgame, fileFormat = templateArr[0]
            filename = f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{pixelgame}_{fileFormat}"
        
        try:
          errospixels, bika, elapsed = await chunk.ImageManipulation.compareImg(
              inter,
              [int(x), int(y)],
              canvas,
              filename,
              tempName,
              "diff",
              pixelgame,
              True,
          )
        except Exception as e:
          print(e)
      
        embed = disnake.Embed(
            title=f"{tempName}",
            url=f"https://www.pixelplanet.fun/#{canvas},{x},{y},10",
            description=f"This took the bot {elapsed:.1f} seconds",
            color=0x00FF00,
        )
        embed.set_author(
            name="erros pixels",
            url="https://www.google.com.br/",
            icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"
        )
        embed.add_field(
                    name="X:", value=f"{x}", inline=True
                )
        embed.add_field(
                            name="Y:", value=f"{y}", inline=True
                        )
        embed.set_image(file=disnake.File("./generated/erros.png"))
        await inter.edit_original_message(embed=embed)
        await inter.wait()

    #@commands.cooldown(1, 5)
    #@commands.slash_command(description='Edits a template.')
    #@commands.has_permissions(ban_members=True, kick_members=True)
    #async def update(self, inter: disnake.ApplicationCommandInteraction, string: str):

    #@update.autocomplete("name")
    #async def erroscomplete(
    #    self, inter: disnake.ApplicationCommandInteraction, string: str
    #):
    #    string = string.lower()
    #    guildFolders = [
    #        filename
    #        for filename in os.listdir("./factions/")
    #        if filename.startswith(f"{inter.guild.id}")
    #    ]
    #    templates = [
    #        temp.split("_")[1]
    #        for temp in os.listdir(f"./factions/{guildFolders[0]}")
    #        if temp.endswith(".png")
    #    ]
    #    print(templates)
    #   return [lang for lang in templates if string in lang.lower()]


    @add.autocomplete("canvas")
    async def canvascomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        string = string.lower()
        canvaslist = ["earth", "1bot", "moon", "top10", "world", "graffiti", "football"]
        return [opt for opt in canvaslist if string in opt.lower()]
    
    @add.autocomplete("pixelgame")
    async def canvascomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        string = string.lower()
        list = ["pixelplanet", "pixelya", "pixelcanvasio"]
        return [opt for opt in list if string in opt.lower()]
    
    @erros.autocomplete("name")
    async def erroscomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        string = string.lower()
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templates = [
            temp.split("_")[1]
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png")
        ]
        print(templates)
        return [lang for lang in templates if string in lang.lower()]

    @remove.autocomplete("name")
    async def namecomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        string = string.lower()
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templates = [
            temp.split("_")[1]
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png")
        ]
        print(templates)
        return [lang for lang in templates if string in lang.lower()]

    @diff.autocomplete("name")
    async def namecomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        string = string.lower()
        guildFolders = [
            filename
            for filename in os.listdir("./factions/")
            if filename.startswith(f"{inter.guild.id}")
        ]
        templates = [
            temp.split("_")[1]
            for temp in os.listdir(f"./factions/{guildFolders[0]}")
            if temp.endswith(".png")
        ]
        return [lang for lang in templates if string in lang.lower()]  


def setup(client):
    client.add_cog(Diff(client))

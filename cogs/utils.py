from funcs.planet import *
from funcs.buttons.pageButton import *

import disnake
from disnake.ext import commands


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Pixelya online counter.")
    async def online(self, inter: disnake.ApplicationCommandInteraction):
        text = ""
        online = await Pixelplanet.get_online(False)

        for i in online:
            text += i + "\n"

        embed = disnake.Embed(color=0xFF0000)
        embed.set_author(
            name="Online",
            icon_url="https://pixelya.fun/PixelyaLOGO.png",
        )
        embed.description = text

        await inter.response.send_message(embed=embed)

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Pixelya daily ranking.")
    async def daily(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
        embeds = []
        ranking = await Pixelplanet.get_daily()

        for j in range(0, 10):
            text = ""

            for i in range(0, 10):
                index = (j * 10) + i
                text += f"#{ranking[index]['dr']} · **{ranking[index]['name']}**: {ranking[index]['dt']}px\n "

            embed = disnake.Embed(color=0x42F57E)
            embed.set_author(
                name="Daily leaderboard",
                icon_url="https://pixelya.fun/PixelyaLOGO.png",
            )
            embed.description = text
            embeds.append(embed)

        if page > 10:
            await inter.response.send_message("The limit is 10.")
        else:
            await inter.response.send_message(
                embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
            )

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Pixelya total ranking.")
    async def total(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
        embeds = []
        ranking = await Pixelplanet.get_ranking()

        for j in range(0, 10):
            text = ""

            for i in range(0, 10):
                index = (j * 10) + i
                text += f"#{ranking[index]['r']} · **{ranking[index]['name']}**: {ranking[index]['t']}px\n "

            embed = disnake.Embed(color=0x5F62E3)
            embed.set_author(
                name="Total leaderboard",
                icon_url="https://pixelya.fun/PixelyaLOGO.png",
            )
            embed.description = text
            embeds.append(embed)

        if page > 10:
            await inter.response.send_message("The limit is 10.")
        else:
            await inter.response.send_message(
                embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
            )


def setup(client):
    client.add_cog(Utils(client))
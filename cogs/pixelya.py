from funcs.planet import *
from funcs.buttons.pageButton import *
from datetime import datetime 

import disnake
from disnake.ext import commands

class Pixelya(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Your Pixelya Profile info.")
    async def perfil(self, inter: disnake.ApplicationCommandInteraction):
        userid = inter.user.id
        username = inter.user.name
         
        try:
            res = await pixelya_funcs.get_profile_by_did(userid)  

            embed = disnake.Embed(color=disnake.Color.green())
            embed.set_author(
                    name=f"@{username}",
                    icon_url="https://pixelya.fun/unknown.png"
            )

            if res[0] == 200:
                p = res[1]
                print(p)

                #
                # check pixels tags
                #
                if p['patent']:
                    try:
                        rep = await pixelya_funcs.get_patent(int(p['patent'][0]))

                        _role = disnake.utils.get(inter.user.roles, name=f"{rep}") #changed
                        if not _role:
                            _role = disnake.utils.get(inter.guild.roles, name=f"{rep}") #changed
                            await inter.user.add_roles(_role)
                            embed1 = disnake.Embed(color=disnake.Color.blue())
                            embed1 = embed1.set_author(name=f'New Tag: "{rep}" set.')
                            await inter.channel.send(embed=embed1)

                    except Exception as e:
                        print(f"Set tag error: {e, sys.exc_info()[2].tb_lineno}")     


                # Faction 
                fac = p['faction']
                if fac:
                    fac = f'{fac[0]} {fac[1]}'
                    try:
                        _role = disnake.utils.get(inter.user.roles, name=f"{fac}") #changed
                        if not _role:
                            _role = disnake.utils.get(inter.guild.roles, name=f"{fac}") #changed
                            await inter.user.add_roles(_role)
                            embed1 = disnake.Embed(color=disnake.Color.blue())
                            embed1 = embed1.set_author(name=f'New Fac: "{fac}" tag set.')
                            await inter.channel.send(embed=embed1)

                    except Exception as e:
                        print(f"Fac set tag error: {e, sys.exc_info()[2].tb_lineno}")     


                #
                # embed
                #
                
                # Avatar
                avatar = p['avatar']
                if avatar == "./unknown.png" or avatar == "/unknown.png":
                    avatar = "https://pixelya.fun/unknown.png"
                # tags
                tags = []
                if len(p["tags"]) > 0:
                    for i in range(len(p["tags"])):
                        tags.append(p["tags"][i][0])
                tags = ', '.join(tags)
                    
                embed.add_field(name="Name:", value=f"{p['namee']}", inline=False)
                embed.add_field(name="Flag", value=f":flag_{p['flag']}:", inline=False)
                embed.add_field(name="Faction: ", value=f"{fac}", inline=True)
                embed.add_field(name="Tags", value=f"{tags}", inline=True)
                embed.add_field(name="Patent: ", value=f"{p['patent'][1]}", inline=False)
                embed.add_field(name="Rank", value=f"{p['ranking']}° ", inline=True)
                embed.add_field(name="TotalPixels: ", value=f"{p['totalPixels']}px", inline=True)
                embed.add_field(name="Daily Rank: ", value=f"{p['dailyRanking']}°", inline=True)
                embed.add_field(name="Daily pixels: ", value=f"{p['dailyTotalPixels']}px", inline=True)
                embed.add_field(name="UserID: ", value=f"{p['id']}", inline=False)
                embed.add_field(name="Registered", value=f"{p['createdAt']}", inline=False)

                embed.set_thumbnail(url=f"{avatar}")
            else:
                embed.color=disnake.Color.red()
                embed.set_author(name=f"{res[1]}")

            await inter.response.send_message(embed=embed)

        except Exception as e:
          print(e, sys.exc_info()[2].tb_lineno)

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Get user Pixelya Profile info.")
    async def user(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        userid = inter.user.id
        username = inter.user.name        
       
        try:
            res = await pixelya_funcs.get_profile_by_did(int(member.id))

            embed = disnake.Embed(color=disnake.Color.green())
            embed.set_author(
                    name=f"Profile Info",
                    icon_url="https://pixelya.fun/unknown.png"
            )
            if res[0] == 200:
                p = res[1]
                print(p)

                # Faction 
                fac = p['faction']
                if fac:
                    fac = f'{fac[0]} {fac[1]}'

                #
                # embed
                #
                
                # Avatar
                avatar = p['avatar']
                if avatar == "./unknown.png" or avatar == "/unknown.png":
                    avatar = "https://pixelya.fun/unknown.png"
                # tags
                tags = []
                if len(p["tags"]) > 0:
                    for i in range(len(p["tags"])):
                        tags.append(p["tags"][i][0])
                tags = ', '.join(tags)
                    
                embed.add_field(name="Name:", value=f"{p['namee']}", inline=False)
                embed.add_field(name="Flag", value=f":flag_{p['flag']}:", inline=False)
                embed.add_field(name="Faction: ", value=f"{fac}", inline=True)
                embed.add_field(name="Tags", value=f"{tags}", inline=True)
                embed.add_field(name="Patent: ", value=f"{p['patent'][1]}", inline=False)
                embed.add_field(name="Rank", value=f"{p['ranking']}° ", inline=True)
                embed.add_field(name="TotalPixels: ", value=f"{p['totalPixels']}px", inline=True)
                embed.add_field(name="Daily Rank: ", value=f"{p['dailyRanking']}°", inline=True)
                embed.add_field(name="Daily pixels: ", value=f"{p['dailyTotalPixels']}px", inline=True)
                embed.add_field(name="UserID: ", value=f"{p['id']}", inline=False)
                embed.add_field(name="Registered", value=f"{p['createdAt']}", inline=False)

                embed.set_thumbnail(url=f"{avatar}")
            else:
                embed.color=disnake.Color.red()
                embed.set_author(name=f"{res[1]}")

            await inter.response.send_message(embed=embed)


        except Exception as e:
          print(e, sys.exc_info()[2].tb_lineno)



    # @commands.cooldown(1, 5)
    # @commands.slash_command()
    # async def daily(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
    #     embeds = []
    #     ranking = await Pixelplanet.get_daily()

    #     for j in range(0, 10):
    #         text = ""

    #         for i in range(0, 10):
    #             index = (j * 10) + i
    #             text += f"#{ranking[index]['dailyRanking']} {ranking[index]['name']}: {ranking[index]['dailyTotalPixels']}px\n "

    #         embed = disnake.Embed(color=0x42F57E)
    #         embed.set_author(
    #             name="Daily leaderboard",
    #             icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
    #         )
    #         embed.description = text
    #         embeds.append(embed)

    #     if page > 10:
    #         await inter.response.send_message("The limit is 10.")
    #     else:
    #         await inter.response.send_message(
    #             embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
    #         )

    # @commands.cooldown(1, 5)
    # @commands.slash_command()
    # async def total(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
    #     embeds = []
    #     ranking = await Pixelplanet.get_ranking()

    #     for j in range(0, 10):
    #         text = ""

    #         for i in range(0, 10):
    #             index = (j * 10) + i
    #             text += f"#{ranking[index]['ranking']} {ranking[index]['name']}: {ranking[index]['totalPixels']}px\n "

    #         embed = disnake.Embed(color=0x5F62E3)
    #         embed.set_author(
    #             name="Total leaderboard",
    #             icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
    #         )
    #         embed.description = text
    #         embeds.append(embed)

    #     if page > 10:
    #         await inter.response.send_message("The limit is 10.")
    #     else:
    #         await inter.response.send_message(
    #             embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
    #         )


def setup(client):
    client.add_cog(Pixelya(client))
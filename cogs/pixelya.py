from funcs.planet import *
from funcs.buttons.pageButton import *
from datetime import datetime 

import disnake
from disnake.ext import commands

class Pixelya(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Your Pixelya profile info.")
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
    @commands.slash_command(description="Get Pixelya user Profile info.")
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


def setup(client):
    client.add_cog(Pixelya(client))
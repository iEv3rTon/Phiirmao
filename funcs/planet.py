import asyncio
from time import time
from io import BytesIO
from pickletools import optimize
import websocket

import httpx, sys
import numpy as np
from PIL import Image, ImageChops, ImageOps
from math import floor
import urllib.request
import disnake
#from funcs.utillis import log_wk

canvas = {
    0: "🌎· Earth",
    1: "🌜· Moon",
    2: "🧱· 3D Canvas",
    3: "🦠· Coronavirus",
    7: "🔲· 1bit",
    8: "🏆· Top10",
}

canvas_convert = {"e": "0", "m": "1", "1": "7"}

class TemplateSt:
    def __init__(self):
        self.totalChunks = 0
        self.madeChunks = 0
        self.messageSent = True
        self.timeMessage = 0
        self.thispc = 20
        self.virginpixels = 0
    def percentage(self):
        return 100*(self.madeChunks/self.totalChunks)
    def thisPercentage(self):
        self.thispc = self.thispc + 20

class Pixelplanet:
    async def get_online() -> list:
        ws = websocket.create_connection("wss://pixelplanet.fun/ws")

        while True:
            data = ws.recv()
            if type(data) != str:
                online = []
                opcode = data[0]
                if opcode == 0xA7:
                    off = len(data)
                    while off > 3:
                        off -= 2
                        first = off
                        off -= 1
                        second = off
                        online.insert(
                            int(data[second]),
                            f"{canvas[int(data[second])]}: {str(int((data[first] << 8) | data[first + 1]))}",
                        )
                    online.insert(0, f"🌎 **Total**: {str((data[1] << 8) | data[2])}\n")

                    break

        ws.close()
        return online

    async def get_daily() -> list:
        players = []
        data = httpx.get("https://pixelplanet.fun/ranking").json()
        for i in range(100):
            player = data["dailyRanking"][i]
            players.append(player)

        return players

    async def get_ranking() -> list:
        players = []
        data = httpx.get("https://pixelplanet.fun/ranking").json()
        for i in range(100):
            player = data["ranking"][i]
            players.append(player)

        return players

class run_preview:
    async def compareImg(message, pixelgame, canvas, x, y, zoom,  diff = None):
        channel = message.channel
        print('run ', pixelgame, canvas, x, y, zoom)
        #log_wk('run ', pixelgame, canvas, x, y, zoom)
        async with channel.typing():

            canvasLink = canvas
            if canvas == "d":
                canvas = 0
            elif canvas == "w" and pixelgame != "pixelya":
                canvas = 7
            elif canvas == "m":
                canvas = 1
            elif canvas == "t":
                canvas = 8
            #pixelya
            elif canvas == "w" and pixelgame == "pixelya":
              canvas = 0
            elif canvas == "g" and pixelgame == "pixelya":
              canvas = 1
            elif canvas == "f" and pixelgame == "pixelya":
              canvas = 2
            

            template = TemplateSt()
            start_time = time()
            
            width, height = int(1000*zoom), int(1000*zoom)
            if diff:
                filename = f"./generated/{pixelgame}.png"
                for attachments in message.attachments:
                    await attachments.save(fp=filename)

                img = Image.open(f"{filename}").convert("RGBA")
                width, height = img.size

            coords = [int(x), int(y)]

            if pixelgame != "pixelcanvas":
                if pixelgame == "pixelplanet":
                    gamelink = "pixelplanet.fun"
                elif pixelgame == "canvaspixel":
                    gamelink = "www.canvaspixel.net"
                elif pixelgame == "pixelya":
                    gamelink = "pixelya.fun"
                else:
                    gamelink = "pixelplanet.fun"
                try:
                    me = httpx.get(f"https://{gamelink}/api/me").json()
                except Exception as e:
                    print(f'game api error: {e}')
                    await channel.send('Game api error', reference=message)
                    return

                colors = me["canvases"][str(canvas)]["colors"]
                csz = me["canvases"][str(canvas)]["size"]
                ch = csz // 2
                c_start_y = (ch + coords[1] - height//2) // 256
                c_start_x = (ch + coords[0] - width//2) // 256
                c_end_y = (ch + coords[1] + height//2) // 256
                c_end_x = (ch + coords[0] + width//2) // 256

                if diff:
                  c_start_y = (ch + coords[1]) // 256
                  c_start_x = (ch + coords[0]) // 256
                  c_end_y = (ch + coords[1] + height) // 256
                  c_end_x = (ch + coords[0] + width) // 256

                c_occupied_y = c_end_y - c_start_y + 1
                c_occupied_x = c_end_x - c_start_x + 1

                size = me["canvases"][str(canvas)]["size"]
                
                image = Image.new("RGB", (c_occupied_x*256, c_occupied_y*256))
                
                async def get_chunk(client, x, y, x_value, y_value):
                    resp = await client.get(
                        f"https://{gamelink}/chunks/{canvas}/{x}/{y}.bmp")
                    resp = resp.content

                    chunk = np.zeros((256, 256, 3), np.uint8)
                    for i, value in enumerate(resp):
                        chunk[i // 256, i % 256] = colors[value] if value < 128 else colors[value - 128]
                    chunk_image = Image.fromarray(chunk, mode="RGB")
                    image.paste(chunk_image, (256*x_value, 256*y_value))
                    template.madeChunks = template.madeChunks + 1
                    if template.percentage() > template.thispc:
                        template.thisPercentage()
                        #await inter.edit_original_message(f'Getting chunks: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')

                async def mainFunc():

                    async with httpx.AsyncClient() as client:

                        tasks = []
                        x_value, y_value = 0, 0
                        for y_index in range(c_start_y, c_end_y+1):
                            for x_index in range(c_start_x, c_end_x+1):
                                tasks.append(asyncio.ensure_future(get_chunk(client, x_index, y_index, x_value, y_value)))
                                template.totalChunks = template.totalChunks + 1
                                x_value += 1
                            y_value += 1
                            x_value = 0
                        #await inter.response.send_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
                        await asyncio.gather(*tasks)
                await mainFunc()
                #await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nBugs are expected, help reporting them on discord.io/phibot")
                c_start_x = (ch + coords[0]) // 256
                c_start_y = (ch + coords[1]) // 256
                start_in_d_x = coords[0] + (ch - (c_start_x) * 256)
                start_in_d_y = coords[1] + (ch - (c_start_y) * 256)

                image = image.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")

                if pixelgame == "pixelplanet":
                    gamelink = f"https://www.pixelplanet.fun/#{canvasLink},{x},{y},10"
                elif pixelgame == "canvaspixel":
                    gamelink = f"https://www.canvaspixel.net/#{canvasLink},{x},{y},10"
                elif pixelgame == "pixelya":
                    gamelink = f"https://pixelya.fun/#{canvasLink},{x},{y},10"
                else:
                    gamelink = f"https://www.pixelplanet.fun/#{canvasLink},{x},{y},10"
            
                if diff:
                    black = Image.new('1', image.size, 0)
                    white = Image.new('1', image.size, 1)
                    mask = Image.composite(white, black, img)

                    def lut(i):
                        return 255 if i > 0 else 0

                    with ImageChops.difference(img, image) as error_mask:
                        error_mask = error_mask.point(lut).convert('L').point(lut).convert('1')
                        error_mask = Image.composite(error_mask, black, mask)

                    tot = np.array(mask).sum()
                    err = np.array(error_mask).sum()
                    
                    img.convert('LA').save("./generated/grayed.png")
                    new_grayed = Image.open("./generated/grayed.png").convert("RGBA")
                    image2 = Image.composite(Image.new('RGBA', image.size, (255, 0, 0)), new_grayed, error_mask).save("./generated/difference.png")
                    
                    #await channel.send(f'***{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)*** \nThis took the bot {(time() - start_time):.1f} seconds.', file=disnake.File('./generated/difference.png'), reference=message)           
                    embed = disnake.Embed(
                        description=f"Placed / Needed \n{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)",
                        color=0x00FF00,
                    )
                    # embed.set_author(
                    #     name=f"This took the bot {(time() - start_time):.1f} seconds",
                    #     url=gamelink,
                    #     icon_url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"                    
                    #     )
                    embed.set_footer(
                        text=f"This took the bot {(time() - start_time):.1f} seconds",
                        #url=gamelink,
                        icon_url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"                    
                    )
                    embed.set_image(file=disnake.File("./generated/difference.png"))
                    await channel.send(embed=embed, reference=message)
                    #return
                
                
                image.save('./generated/bigchunks.png')
                embed = disnake.Embed(
                        color=0x00FF00,
                    )
                embed.set_footer(
                        text=f"This took the bot {(time() - start_time):.1f} seconds",
                        #url=gamelink,
                        icon_url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"                    
                    )
                embed.set_image(file=disnake.File("./generated/bigchunks.png"))
                await channel.send(embed=embed, reference=message)
                return

            else:
                try:
                    print('pixelcanvas suport')
                
                    #await inter.response.send_message('Starting... Please wait.')
                    w, h = width, height
                    xi, yi = coords[0], coords[1]
            
                    # firstChunkY = (coords[1] - h//2) // 512
                    # firstChunkX = (coords[0] - w//2) // 512
                    # lastChunkY = (coords[1] + h//2) // 512
                    # lastChunkX = (coords[0] + w//2) // 512

                    # if diff:
                    firstChunkY = (coords[1]) // 512
                    firstChunkX = (coords[0]) // 512
                    lastChunkY = (coords[1] + h) // 512
                    lastChunkX = (coords[0] + w) // 512

                    chunksYtoGet = lastChunkY - firstChunkY + 1
                    chunksXtoGet = lastChunkX - firstChunkX + 1

                    image = Image.new('RGB', (512*chunksXtoGet, 512*chunksYtoGet))
                    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36'}

                    chunks_to_get = []
                    async def get_chunk_pc(client, x, y, chunksXGot, chunksYGot):
                        url = f"https://pixelcanvas.io/tile/{x*512}/{y*512}.png"
                        req = urllib.request.Request(url, headers=header)
                        chunk = Image.open(urllib.request.urlopen(req))
                        image.paste(chunk, (512*chunksXGot, 512*chunksYGot))
                        template.madeChunks = template.madeChunks + 1
                        if template.percentage() > template.thispc:
                            template.thisPercentage()
                    
                    async def mainFunc_pc():
                        async with httpx.AsyncClient() as client:

                            tasks = []
                            chunksXGot, chunksYGot = 0, 0
                            x_, y_ = 0, 0
                            for y_ in range(firstChunkY, firstChunkY+chunksYtoGet):
                                for x_ in range(firstChunkX, firstChunkX+chunksXtoGet):
                                    tasks.append(asyncio.ensure_future(get_chunk_pc(client, x_, y_, chunksXGot, chunksYGot)))
                                    template.totalChunks = template.totalChunks + 1
                                    chunksXGot = chunksXGot + 1
                                    chunks_to_get.append([xi+x_,yi+y_])
                                chunksXGot = 0
                                chunksYGot = chunksYGot + 1

                            await asyncio.gather(*tasks)
                    await mainFunc_pc()

                    CoordXi = abs((firstChunkX*512)-xi)
                    CoordYi = abs((firstChunkY*512)-yi)
                    CoordwCrop, CoordhCrop = w, h

                    image = image.crop((CoordXi, CoordYi, CoordXi+CoordwCrop, CoordYi+CoordhCrop)).convert('RGBA')

                    gamelink = f"https://pixelcanvas.io/@{x},{y},0"
                    if diff:
                        black = Image.new('1', image.size, 0)
                        white = Image.new('1', image.size, 1)
                        mask = Image.composite(white, black, img)

                        def lut(i):
                            return 255 if i > 0 else 0

                        with ImageChops.difference(img, image) as error_mask:
                            error_mask = error_mask.point(lut).convert('L').point(lut).convert('1')
                            error_mask = Image.composite(error_mask, black, mask)

                        tot = np.array(mask).sum()
                        err = np.array(error_mask).sum()
                        
                        img.convert('LA').save("./generated/grayed.png")
                        new_grayed = Image.open("./generated/grayed.png").convert("RGBA")
                        image2 = Image.composite(Image.new('RGBA', image.size, (255, 0, 0)), new_grayed, error_mask).save("./generated/difference.png")
                        
                        embed = disnake.Embed(
                            description=f"Placed / Needed \n{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)",
                            color=0x00FF00,
                        )
                        embed.set_footer(
                            text=f"This took the bot {(time() - start_time):.1f} seconds",
                            #url=gamelink,
                            icon_url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"                    
                        )
                        embed.set_image(file=disnake.File("./generated/difference.png"))
                        await channel.send(embed=embed, reference=message)    
                        return
                    else:
                        image.save('./generated/bigchunks.png')
                        embed = disnake.Embed(
                            color=0x00FF00,
                        )
                        embed.set_footer(
                            text=f"This took the bot {(time() - start_time):.1f} seconds",
                            #url=gamelink,
                            icon_url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"                    
                        )
                        embed.set_image(file=disnake.File("./generated/bigchunks.png"))
                        await channel.send(embed=embed, reference=message)    
                        return
                except Exception as e:
                    print(e, sys.exc_info()[2].tb_lineno)


class PlanetHistory:
    def __init__(self, canvas, start, filename, day, month, year):
        self.canvas = canvas_convert[canvas]
        self.day = day
        self.month = month
        self.year = year
        self.imgs = []

        template = TemplateSt()

        img = Image.open(f"{filename}").convert("RGBA")
        size = img.size

        me = httpx.get("https://pixelplanet.fun/api/me").json()
        csz = me["canvases"][self.canvas]["size"]
        ch = csz // 2

        self.start_y = (ch + int(start[1])) // 256
        self.start_x = (ch + int(start[0])) // 256
        self.last_y = ((ch + int(start[1]) + size[0]) // 256) + 1
        self.last_x = ((ch + int(start[0]) + size[1]) // 256) + 1

    # async def get_history_chunk(self, client, x: int, y: int, time: str, img) -> None:
    #     template = TemplateSt()
    #     time = time if not time == "tile" else "tiles"
    #     resp = await client.get(
    #         f"https://storage.pixelplanet.fun/{self.year}/{self.month}/{self.day}/{self.canvas}/{time}/{str(x)}/{str(y)}.png"
    #     )

    #     if resp.status_code == 200:
    #         img.paste(
    #             Image.open(BytesIO(resp.content)),/
    #             (256 * (x - self.start_x), 256 * (y - self.start_y)),
    #         )
    #     template.madeChunks = template.madeChunks + 1
    #     if template.percentage() > template.thispc:
    #         template.thisPercentage()
    #         await inter.edit_original_message(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')
        

    # async def get_chunks_blob(self, time) -> None:
    #     await inter.response.send_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
    #     async with httpx.AsyncClient() as client:
    #         tasks = []
    #         img = Image.new(
    #             "RGBA",
    #             (
    #                 256 * (self.last_x - self.start_x),
    #                 256 * (self.last_y - self.start_y),
    #             ),
    #             (255, 0, 0, 0),
    #         )

    #         for y_index in range(self.start_y, self.last_y):
    #             for x_index in range(self.start_x, self.last_x):
    #                 template.totalChunks = template.totalChunks + 1
    #                 tasks.append(
    #                     asyncio.ensure_future(
    #                         self.get_history_chunk(client, x_index, y_index, time, img)
    #                     )
    #                 )
    #         await asyncio.gather(*tasks)
    #         self.imgs.append(img)
    #         await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nMaking your gif")

    # async def make_images(self) -> None:
    #     start = time.time()
    #     async with httpx.AsyncClient() as client:
    #         resp = await client.get(
    #             f"https://pixelplanet.fun/history?day={self.year}{self.month}{self.day}&id=0"
    #         )
    #         tasks = []
    #         if resp.status_code == 200:
    #             times = resp.json()
    #             for i in times:
    #                 tasks.append(asyncio.ensure_future(self.get_chunks_blob(i)))

    #             await asyncio.gather(*tasks)

    #             await self.save_gif()
    #             return time.time() - start

    # async def save_gif(self) -> None:
    #     async with httpx.AsyncClient() as client:
    #         tasks = []
    #         img = Image.new(
    #             "RGBA",
    #             (
    #                 256 * (self.last_x - self.start_x),
    #                 256 * (self.last_y - self.start_y),
    #             ),
    #             (255, 0, 0, 0),
    #         )

    #         for y_index in range(self.start_y, self.last_y):
    #             for x_index in range(self.start_x, self.last_x):
    #                 tasks.append(
    #                     asyncio.ensure_future(
    #                         self.get_history_chunk(
    #                             client, x_index, y_index, "tile", img
    #                         )
    #                     )
    #                 )

    #         await asyncio.gather(*tasks)
    #         img.save(
    #             "teste.gif",
    #             save_all=True,
    #             append_images=self.imgs,
    #             optimize=True,
    #             duration=80,
    #             loop=0,
    #         )

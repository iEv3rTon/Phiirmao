import asyncio
from time import time

import httpx, sys
import numpy as np
from PIL import Image, ImageChops, ImageOps
from math import floor
import urllib.request

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

class ImageManipulation:
    async def compareImg(inter, coords, canvas, filename, tempName, version, pixelgame, erros_ = False):
        if canvas == "e":
            canvas = 0
        elif canvas == "1":
            canvas = 7
        elif canvas == "m":
            canvas = 1
        elif canvas == "t":
            canvas = 8
        #pixelya
        elif canvas == "w":
          canvas = 0
        elif canvas == "g":
          canvas = 1
        elif canvas == "f":
          canvas = 2
  
        template = TemplateSt()
        start_time = time()
        img = Image.open(f"{filename}").convert("RGBA")
        width, height = img.size

        if pixelgame != "pixelcanvasio":
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
                await inter.response.send_message('Game api error')
                return

            colors = me["canvases"][str(canvas)]["colors"]
            csz = me["canvases"][str(canvas)]["size"]
            ch = csz // 2
            c_start_y = (ch + coords[1]) // 256
            c_start_x = (ch + coords[0]) // 256
            c_end_y = (ch + coords[1] + height) // 256
            c_end_x = (ch + coords[0] + width) // 256

            c_occupied_y = c_end_y - c_start_y + 1
            c_occupied_x = c_end_x - c_start_x + 1

            size = me["canvases"][str(canvas)]["size"]
            if version == 'diff':
                image = Image.new("RGB", (c_occupied_x*256, c_occupied_y*256))
            elif version == 'virgins':
                virgins = Image.new("RGBA", (c_occupied_x*256, c_occupied_y*256))
            else:
                protected = Image.new("RGBA", (c_occupied_x*256, c_occupied_y*256))

            async def get_chunk(client, x, y, x_value, y_value):
                resp = await client.get(
                    f"https://{gamelink}/chunks/{canvas}/{x}/{y}.bmp")
                resp = resp.content

                if version == 'diff':
                    chunk = np.zeros((256, 256, 3), np.uint8)
                    for i, value in enumerate(resp):
                        chunk[i // 256, i % 256] = colors[value] if value < 128 else colors[value - 128]
                    chunk_image = Image.fromarray(chunk, mode="RGB")
                    image.paste(chunk_image, (256*x_value, 256*y_value))
                elif version == 'virgins':
                    virginchunk = np.zeros((256, 256, 4), np.uint8)
                    for i, value in enumerate(resp):   
                        virginchunk[i // 256, i % 256] = [0,255,0,255] if value == 0 or value == 1 else [0,0,0,0]
                        template.virginpixels = template.virginpixels + 1 if value == 0 or value == 1 else template.virginpixels
                
                    virgin_image = Image.fromarray(virginchunk, mode="RGBA")
                    virgins.paste(virgin_image, (256*x_value, 256*y_value))
                else:
                    protectedchunk = np.zeros((256, 256, 4), np.uint8)
                    for i, value in enumerate(resp): 
                        protectedchunk[i // 256, i % 256] = [0,255,255,255] if value > 127 else [0,0,0,0]
                    protected_image = Image.fromarray(protectedchunk, mode="RGBA")
                    protected.paste(protected_image, (256*x_value, 256*y_value))
                template.madeChunks = template.madeChunks + 1
                if template.percentage() > template.thispc:
                    template.thisPercentage()
                    await inter.edit_original_message(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')

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
                    await inter.response.send_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
                    await asyncio.gather(*tasks)
            await mainFunc()
            await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nBugs are expected, help reporting them on discord.io/phibot")
            c_start_x = (ch + coords[0]) // 256
            c_start_y = (ch + coords[1]) // 256
            start_in_d_x = coords[0] + (ch - (c_start_x) * 256)
            start_in_d_y = coords[1] + (ch - (c_start_y) * 256)

            if version == 'diff':
                image = image.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
            elif version == 'virgins':
                virgins = virgins.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
            else:
                protected = protected.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
            if version == 'diff':
                black = Image.new('1', image.size, 0)
                white = Image.new('1', image.size, 1)
                mask = Image.composite(white, black, img)

                def lut(i):
                    return 255 if i > 0 else 0

                #pika = ImageChops.difference(img, image)
                #pika.save('pika.png')
                if erros_:
                    diff = Image.new('RGBA', (width, height))
                    pixels = []
                    
                    for y in range(height):
                        for x in range(width):
                            ri, gi, bi, ai = img.getpixel((x,y))
                            rc, gb, bc, ac = image.getpixel((x,y))
                            if ai == 0:
                                pixels.append((0, 0, 0, 0))
                                continue
            
                            if ri == rc and gi == gb and bi == bc:
                                pixels.append((0, 0, 0, 0))
                                continue
            
                            pixels.append((ri, gi, bi, 255))
            
                    diff.putdata(pixels)
                    diff.save('./generated/erros.png')
        
                with ImageChops.difference(img, image) as error_mask:
                    error_mask = error_mask.point(lut).convert('L').point(lut).convert('1')
                    error_mask = Image.composite(error_mask, black, mask)

                tot = np.array(mask).sum()
                err = np.array(error_mask).sum()
                image.save('./generated/bigchunks.png')
            elif version == 'virgins':
                    pass
            else:
                    pass
            img.convert('LA').save("./generated/grayed.png")
            new_grayed = Image.open("./generated/grayed.png").convert("RGBA")
            if version == 'diff':
                image2 = Image.composite(Image.new('RGBA', image.size, (255, 0, 0)), new_grayed, error_mask).save("./generated/difference.png")
                return tot, err, (time() - start_time)
            elif version == 'virgins':
                image3 = Image.composite(Image.new('RGBA', virgins.size, (0, 255, 0)), new_grayed, virgins).save("./generated/virgins.png")
                print(f'virginpixels =`{template.virginpixels}')
                return template.virginpixels, (time() - start_time)
            else:
                image4 = Image.composite(Image.new('RGBA', image.size, (0, 0, 255)), new_grayed, protected).save("./generated/protected.png")

        else:
            try:
                print('pixelcanvas suport')
                if version != 'diff' or erros_:
                    await inter.response.send_message('This command not supported in PixelCanvas.io!')
                    return

                await inter.response.send_message('Starting... Please wait.')
                w, h = width, height
                xi, yi = coords[0], coords[1]
          
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
                        await inter.edit_original_message(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')
                        #print(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')

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

                        await inter.edit_original_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
                        #print(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
                        await asyncio.gather(*tasks)
                await mainFunc_pc()

                await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nBugs are expected, help reporting them on discord.io/phibot")
                #print(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nBugs are expected, help reporting them on discord.io/phibot")

                CoordXi = abs((firstChunkX*512)-xi)
                CoordYi = abs((firstChunkY*512)-yi)
                CoordwCrop, CoordhCrop = w, h

                image = image.crop((CoordXi, CoordYi, CoordXi+CoordwCrop, CoordYi+CoordhCrop)).convert('RGBA')

                #print('size: ', image.size, img.size)
            
                black = Image.new('1', image.size, 0)
                white = Image.new('1', image.size, 1)
                mask = Image.composite(white, black, img)

                def lut_(i):
                    return 255 if i > 0 else 0
                
                with ImageChops.difference(img, image) as error_mask:
                    error_mask = error_mask.point(lut_).convert('L').point(lut_).convert('1')
                    error_mask = Image.composite(error_mask, black, mask)

                tot = np.array(mask).sum()
                err = np.array(error_mask).sum()
                image.save('./generated/bigchunks.png')

                img.convert('LA').save("./generated/grayed.png")
                new_grayed = Image.open("./generated/grayed.png").convert("RGBA")

                image2 = Image.composite(Image.new('RGBA', image.size, (255, 0, 0)), new_grayed, error_mask).save("./generated/difference.png")
                
                #print( tot, err, (time() - start_time))

                return tot, err, (time() - start_time)
            except Exception as e:
                print(e, sys.exc_info()[2].tb_lineno)

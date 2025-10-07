import os
import re
import random
import aiohttp
import aiofiles
import traceback

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def truncate(text):
    list = text.split(" ")
    text1, text2 = "", ""
    for i in list:
        if len(text1) + len(i) < 30:
            text1 += " " + i
        elif len(text2) + len(i) < 30:
            text2 += " " + i
    return [text1.strip(), text2.strip()]


async def get_thumb(videoid: str):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        icons = Image.open("AloneMusic/assets/icons.png")
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        # Cinematic background
        background = image2.filter(ImageFilter.GaussianBlur(25))
        background = ImageEnhance.Brightness(background).enhance(0.55)
        background = ImageEnhance.Contrast(background).enhance(1.2)

        # Logo crop and shadow
        Xcenter, Ycenter = youtube.width / 2, youtube.height / 2
        x1, y1 = Xcenter - 250, Ycenter - 250
        x2, y2 = Xcenter + 250, Ycenter + 250
        rand_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((370, 370), Image.ANTIALIAS)
        shadow = ImageOps.expand(logo, border=20, fill=(0, 0, 0))
        background.paste(shadow, (95, 145), shadow)
        background.paste(logo, (100, 150), logo)

        # Drawing text
        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("AloneMusic/assets/font2.ttf", 32)
        font = ImageFont.truetype("AloneMusic/assets/font.ttf", 32)
        tfont = ImageFont.truetype("AloneMusic/assets/font3.ttf", 48)

        stitle = truncate(title)
        draw.text((565, 180), stitle[0], (255, 255, 255), font=tfont)
        draw.text((565, 240), stitle[1], (255, 255, 255), font=tfont)
        draw.text((565, 330), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)

        # Dynamic gradient line (subtle animation effect)
        line_start_x, line_end_x = 565, 1130
        for i in range(line_start_x, line_end_x, 2):
            blend = int((i - line_start_x) / (line_end_x - line_start_x) * 255)
            draw.line([(i, 400), (i, 400)], fill=(blend, blend, 255), width=6)

        draw.ellipse([(999, 390), (1015, 405)], outline=rand_color, fill=rand_color, width=10)
        draw.text((565, 420), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 420), f"{duration[:23]}", (255, 255, 255), font=arial)

        # Paste icons
        picons = icons.resize((580, 62))
        background.paste(picons, (565, 460), picons)

        # Remove temp thumbnail
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except:
        traceback.print_exc()
        return None

import filer

import python_weather
import asyncio
from PIL import Image, ImageDraw, ImageFont

async def get_weather(city: str):
    weather_client = python_weather.Client(format=python_weather.IMPERIAL)
    weather = await weather_client.find(city)

    await weather_client.close()

    return (weather.current.feels_like, weather.current.sky_text)

def get_weather_icon(weather: str, size: tuple):
    # return new icon image as Image
    icon_w = 600/3
    icon_h = 564/3
    if weather == "Sunny" or weather == "Mostly Sunny" or weather == "Partly Sunny":
        source_box = (2*icon_w, 2*icon_h, 3*icon_w, 3*icon_h)
    elif weather == "Rain" or weather == "Rain Showers" or weather == "Light Rain And Snow" or weather == "Light Rain":
        source_box = (0, 0, icon_w, icon_h)
    elif weather == "Snow" or weather == "Snow Showers" or weather == "Light Snow":
        source_box = (2*icon_w, 0, 3*icon_w, icon_h)
    elif weather == "Cloudy" or weather == "Mostly Cloudy":
        source_box = (icon_w, 0, 2*icon_w, icon_h)
    elif weather == "T-Storms":
        source_box = (0, icon_h, icon_w, 2*icon_h)
    else:
        with Image.open(filer.base() + 'data/erroricon.png') as img:
            img.resize(size, Image.BILINEAR)
            img.save(filer.base() + 'icon.png')

    with Image.open(filer.base() + 'data/weathericons.png') as img:
        img = img.resize(size, Image.BILINEAR, source_box)
        img.save(filer.base() + 'icon.png')

def get_temp_img(temperature: int, height: int): # width is dynamically set
    mono_font = ImageFont.truetype(filer.base() + 'data/Courier Prime Bold.ttf', size=height)

    img = Image.new('RGB', (mono_font.getsize('xx')[0], height), 0)

    graphics = ImageDraw.Draw(img)
    graphics.text((0, 5), str(temperature), fill=(255,255,255), font=mono_font)

    img.save(filer.base() + 'text.png')

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    (temp, weather) = asyncio.run(get_weather("new york city"))

    print(temp, weather + ".")
import datetime
import filer

import python_weather
import asyncio
from PIL import Image, ImageDraw, ImageFont

async def get_weather(city: str):
    weather_client = python_weather.Client(format=python_weather.IMPERIAL)
    weather = await weather_client.find(city)

    await weather_client.close()

    return (weather.current.temperature, weather.current.sky_text)

def get_weather_icon(weather: str, size: tuple):
    # return new icon image as Image
    icon_w = 600/3
    icon_h = 564/3

    sun_icon = ["Clear", "Mostly Clear", "Partly Clear", "Sunny", "Mostly Sunny", "Partly Sunny"]
    rain_icon = ["Rain", "Rain Showers", "Light Rain And Snow", "Light Rain"]
    snow_icon = ["Snow", "Snow Showers", "Light Snow"]
    cloud_icon = ["Cloudy", "Mostly Cloudy", "Partly Cloudy"]
    storm_icon = ["T-Storms"]

    if weather in sun_icon:
        source_box = (2*icon_w, 2*icon_h, 3*icon_w, 3*icon_h)
    elif weather in rain_icon:
        source_box = (0, 0, icon_w, icon_h)
    elif weather in snow_icon:
        source_box = (2*icon_w, 0, 3*icon_w, icon_h)
    elif weather in cloud_icon:
        source_box = (icon_w, 0, 2*icon_w, icon_h)
    elif weather in storm_icon:
        source_box = (0, icon_h, icon_w, 2*icon_h)
    else:
        print("Unsupported weather type:", weather)
        with Image.open(filer.base() + 'data/erroricon.png') as img:
            img.resize(size, Image.BILINEAR)
            img.save(filer.base() + 'icon.png')
            return

    with Image.open(filer.base() + 'data/weathericons.png') as img:
        img = img.resize(size, Image.BILINEAR, source_box)
        img.save(filer.base() + 'icon.png')

def get_temp_img(temperature: int, height: int): # width is dynamically set
    mono_font = ImageFont.truetype(filer.base() + 'data/Courier Prime Bold.ttf', size=height)

    img = Image.new('RGB', (mono_font.getsize('xxxx')[0], height), 0)

    graphics = ImageDraw.Draw(img)
    graphics.text((0, 5), str(temperature) + '°F', fill=(255, 255, 255), font=mono_font)

    img.save(filer.base() + 'text.png')

def get_date_img(height: int):
    date = datetime.datetime.now().strftime("%m/%d")

    mono_font = ImageFont.truetype(filer.base() + 'data/Courier Prime Bold.ttf', size=height)

    img = Image.new('RGB', (mono_font.getsize('xxxxx')[0], height), 0)

    graphics = ImageDraw.Draw(img)
    graphics.text((0, 5), date, fill=(255, 255, 255), font=mono_font)

    img.save(filer.base() + 'date.png')
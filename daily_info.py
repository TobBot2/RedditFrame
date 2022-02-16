import python_weather
import asyncio
from PIL import Image, ImageOps

async def get_weather(city: str):
    weather_client = python_weather.Client(format=python_weather.IMPERIAL)
    weather = await weather_client.find(city)

    await weather_client.close()

    return (weather.current.feels_like, weather.current.sky_text)

def get_weather_icon(weather: str, size: tuple):
    # return new icon image as Image
    icon_w = 600/3
    icon_h = 564/3
    if weather == "Sunny" or "Mostly sunny" or "Partly sunny":
        source_box = (2*icon_w, 2*icon_h, 3*icon_w, 3*icon_h)
    elif weather == "Rain" or "Rain showers" or "Light rain and snow" or "Light rain":
        source_box = (0, 0, icon_w, icon_h)
    elif weather == "Snow" or "Snow showers" or "Light Snow":
        source_box = (2*icon_w, 0, 3*icon_w, icon_h)
    elif weather == "Cloudy" or "Mostly cloudy":
        source_box = (icon_w, 0, 2*icon_w, icon_h)
    elif weather == "T-storms":
        source_box = (0, icon_h, icon_w, 2*icon_h)
    else:
        with Image.open('erroricon.png') as img:
            img.resize(size, Image.BILINEAR)
            return img

    with Image.open('weathericons.png') as img:
        img = img.resize(size, Image.BILINEAR, source_box)
        return img

def get_temp_img(temperature: int, size: tuple):
    img = Image.new('RGB', size)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_weather("new york city"))
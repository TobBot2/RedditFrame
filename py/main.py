import best_reddit
import process_image
import daily_info

import time
import asyncio
import sys
import traceback

if sys.platform == 'linux':
    import epaper_display

def main(index: int = None):
    # return True if successful
    subreddit = best_reddit.get_subreddit(index)
    posts = best_reddit.get_top_n_json(subreddit, 10, 'week')

    (temp, weather) = asyncio.run(daily_info.get_weather("new york city"))
    
    # save info as images of size ___
    daily_info.get_weather_icon(weather, (50, 50))
    daily_info.get_temp_img(temp, 50)

    for candidate_post in posts:
        if best_reddit.recently_viewed(candidate_post['id']):
            continue

        if not create_screen_png((480, 800), candidate_post):
            continue

        if sys.platform == 'linux':
            epaper_display.display_vertical()
        elif sys.platform == 'win32':
            print('rendered image')

        best_reddit.trim_viewed(360)
        return True
    return False

def create_screen_png(screen_size: tuple, post):
    # return True if successful
    try:
        process_image.get_image_from_url(post['img_url'])
        (bar_size, is_vertical, is_reject) = process_image.resize_with_bars(screen_size)

        if is_reject:
            return False
        
        title_height = bar_size
        if not is_vertical: title_height = 0
        best_reddit.get_title_as_img(post['title'], (screen_size[0], title_height))

        process_image.FS_dithering()
        process_image.reapply_bars(bar_size, is_vertical)

        process_image.FS_dithering('icon.png')
        process_image.FS_dithering('text.png')

        process_image.overlay_image('icon.png', (screen_size[0] - 60, screen_size[1] - 60))
        process_image.overlay_image('text.png', (screen_size[0] - 180, screen_size[1] - 60))
        process_image.overlay_image('title.png', (0, 0))

        return True
    except Exception as e:
            with open('C:/Users/trevo/Documents/Coding/Python/Reddit Frame/data/errors.txt') as f:
                errors = f.readlines()

            if (str(e) + "\n") not in errors: # + "\n" because it's included when doing f.readlines()
                print("unexpected error: \n")
                traceback.print_exc()
                exit()

            print("expected error (" + str(e) + ")")
            return False

def valid_image(index: int = None):
    tries = 0 # added so if there's no compatible images in a subreddit, it just fails
    while True:
        if main(index) or tries > 15:
            tries = 0
            return
        tries += 1

def loop_random(times):
    for i in range(times):
        valid_image()
        if sys.platform == 'linux':
            time.sleep(180) # refresh rate should be at least 180 seconds per manual's request
        elif sys.platform == 'win32':
            time.sleep(5)

def loop_all():
    # only run for testing
    for i in range(24):
        valid_image(i)
        time.sleep(5)

def infinite_cycle(refresh_rate: int):
    while True:
        valid_image
        time.sleep(refresh_rate)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    #loop_all()
    loop_random(10)
    # hours_between_refresh = 3
    # infinite_cycle(60*60*hours_between_refresh)
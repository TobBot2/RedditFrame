import best_reddit as best_reddit
import process_image
import daily_info
import filer
import epaper_display

import time
import asyncio

def main(index: int = None):
    subreddit = best_reddit.get_subreddit(index)
    posts = best_reddit.get_top_n_json(subreddit, 10, 'day')

    (temp, weather) = asyncio.run(daily_info.get_weather("new york city"))
    
    # save info as images of size ___
    daily_info.get_weather_icon(weather, (50, 50))
    daily_info.get_temp_img(temp, 50)

    for candidate_post in posts:
        if candidate_post['img_url'] == None:
            continue

        try:
            create_screen_png((480, 800), candidate_post)
            print('Image Rendered')
            epaper_display.display_vertical()
            print('Image Displayed')
            time.sleep(30)
        except Exception as e:
            print('error:', e)

def create_screen_png(screen_size: tuple, post):
    process_image.get_image_from_url(post['img_url'])
    (bar_size, is_vertical, is_reject) = process_image.resize_with_bars(screen_size)

    if is_reject:
        # okay this shouldn't raise an exception but it should be handled the same way as an exception so here we are
        raise Exception("image aspect ratio is too different")

    process_image.FS_dithering()
    process_image.reapply_bars(bar_size, is_vertical)

    process_image.FS_dithering('icon.png')
    process_image.FS_dithering('text.png')

    process_image.overlay_image('icon.png', (420, 740))
    process_image.overlay_image('text.png', (360, 740))

    process_image.set_for_epaper()

def loop_all(start_at: int = 0):
    with open(filer.base() + 'data/subreddits.csv', 'r') as f:
        length = len(f.read().split(','))
    
    for i in range(length - start_at):
        main(i + start_at)
        time.sleep(5)

def loop_random(times):
    for i in range(times):
        main()

if __name__ == "__main__":
    loop_random(10)
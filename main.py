import best_reddit
import process_image
import daily_info
import time
import asyncio
from PIL import Image

def main(index: int = None):
    subreddit = best_reddit.get_subreddit(index)
    posts = best_reddit.get_top_n_json(subreddit, 10, 'day')

    #(temp, weather) = asyncio.run(daily_info.get_weather("new york city"))
    weather_icon = daily_info.get_weather_icon('Sunny', (50, 50))
    temp_img = daily_info.get_temp_img(30, (50, 50))

    for candidate_post in posts:
        if candidate_post['img_url'] == None: continue
        post = candidate_post

        try:
            create_screen_png((480, 800), post, weather_icon, temp_img).save('cuteness.png')
        except Exception as e:
            print('error:', e)

def create_screen_png(screen_size: tuple[int, int], post, weather_icon: Image.Image, temp_img: Image.Image):
    final_img = process_image.get_image_from_url(post['img_url'])
    (final_img, bar_size, is_vertical, is_reject) = process_image.resize_with_bars(final_img, screen_size)

    final_img = process_image.reapply_bars(final_img, bar_size, is_vertical)
    final_img = process_image.FS_dithering(final_img)

    final_img = process_image.overlay_image(final_img, process_image.FS_dithering(weather_icon), (420, 740))
    final_img = process_image.overlay_image(final_img, process_image.FS_dithering(temp_img), (360, 740))

    return final_img

def loop_all(start_at: int = 0):
    with open('subreddits.csv', 'r') as f:
        length = len(f.read().split(','))
    
    for i in range(length - start_at):
        main(i + start_at)
        time.sleep(5)
def loop_random(times):
    for i in range(times):
        main()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop_all()
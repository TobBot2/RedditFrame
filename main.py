import best_reddit
import process_image
import time

def main(index):
    subreddit = best_reddit.get_subreddit(index)
    print('Subreddit chosen:', subreddit)
    posts = best_reddit.get_top_n_json(subreddit, 15, 'week')

    post = None
    for candidate_post in posts:
        if candidate_post['img_url'] == None:
            continue
        post = candidate_post
        
        print('Post chosen:', post['title'], post['img_url'])
        try:
            process_image.save_image_to_file(post['img_url'])
            process_image.resize_and_crop((480, 800))
            process_image.FS_dithering()
            time.sleep(5)
        except Exception as e:
            print('failed to get, resize or dither image', e)

def loop_all(start_at = 0):
    with open('subreddits.csv') as f:
        length = len(f.read().split(','))
    
    for i in range(length - start_at):
        main(i + start_at)
        time.sleep(5)

if __name__ == "__main__":
    loop_all()
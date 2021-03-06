import filer

import requests
import random
from PIL import Image, ImageOps, ImageFont, ImageDraw

def get_subreddit(index: int = None):
    with open(filer.base() + 'data/subreddits.csv', 'r') as f:
        subreddits = f.read().split(',')

    if index != None:
        return subreddits[index]

    return random.choice(subreddits)

def get_top_n_json(subreddit: str, n: int, time_frame: str):
    # returns useful information in the post
    # get json
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/top.json?limit={n}&t={time_frame}'
        request_get = requests.get(base_url, headers = {'User-agent': 'yourbot'})
    except:
        print('Error requesting JSON')
        return
    
    json = request_get.json()

    # get titles of posts
    titles = []
    for post in json['data']['children']:
        titles.append(post['data']['title'])

    # get image urls of posts (use None if it is not an image)
    image_urls = []
    for post in json['data']['children']:
        # return if media is a video (media will be null if it is an image)
        if (post['data']['media'] != None):
            image_urls.append(None)
            continue

        image_urls.append(post['data']['url'])
    
    ids = []
    for post in json['data']['children']:
        ids.append(post['data']['id'])

    # combine data
    posts = []
    for i in range(len(titles)): # use length of titles because not gaurunteed to return up to limit
        posts.append({'title': titles[i], 'img_url': image_urls[i], 'id': ids[i]})

    return posts

def recently_viewed(post_id: str):
    # return true if recently seen
    with open(filer.base() + 'data/viewed.csv', 'r') as f:
        data = f.read()
        seen_ids = str(data).split(',')
    
    if post_id in seen_ids:
        return True

    # haven't seen it -> add to beginning of list and return false
    with open(filer.base() + 'data/viewed.csv', 'w') as f:
        f.write(post_id + ',' + data)
        
    return False

def trim_viewed(trim_to: int):
    # cuts out earlier elements first
    with open(filer.base() + 'data/viewed.csv', 'r') as f:
        data = f.read()
        data_list = str(data).split(',')

    data_len = len(data_list)
    if data_len <= trim_to:
        return # already trimmed!
        
    new_data = ''
    for i in range(trim_to):
        new_data += data_list[i] + ','
        
    with open(filer.base() + 'data/viewed.csv', 'w') as f:
        f.write(new_data)


def get_title_as_img(title: str, size: tuple):
    # TODO set text size based on characters. Constrain to input size
    padding = (10, 10)
    adjusted_size = (size[0] - padding[0]*2, size[1] - padding[1]*2)

    mono_font = None
    formatted_title = ""
    for i in range(5):
        char_height = int(adjusted_size[1] / (i+1))

        if char_height < 20:
            char_height = 20

        mono_font = ImageFont.truetype(filer.base() + 'data/Courier Prime Bold.ttf', char_height)
        char_width = mono_font.getsize('x')[0]

        x_characters = int(adjusted_size[0] / char_width)
        y_characters = int(adjusted_size[1] / char_height)

        nl_candidate = 0
        used_chars = 0
        title_candidate = title
        for y in range(y_characters):
            add_newline = False
            for x in range(min(x_characters, len(title_candidate) - used_chars)):
                if title_candidate[used_chars + x] == ' ':
                    nl_candidate = x
                    add_newline = True

            if not add_newline:
                break # no adequate new lines, must shrink font size

            used_chars += nl_candidate + 1 # + 1 because new line is two chars
            title_candidate = title_candidate[:used_chars-1] + '\n' + title_candidate[used_chars:]

        formatted_title = title_candidate
        
        if len(title_candidate.split('\n')[-1]) <= x_characters:
            break # fits! stop shrinking now

    final_size = mono_font.getsize_multiline(formatted_title)

    img = Image.new('RGB', (max(final_size[0] + padding[0]*2, size[0]), final_size[1] + padding[1]*2), 0)
    graphics = ImageDraw.Draw(img)

    graphics.text(padding, formatted_title, fill=(255,255,255), font=mono_font)

    img.save(filer.base() + 'title.png')
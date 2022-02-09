import requests
import random

def get_subreddit(index = None):
    with open('subreddits.csv', 'r') as f:
        subreddits = f.read().split(',')

    if index != None:
        return subreddits[index]

    random_index = random.randint(0, len(subreddits) - 1)
    return subreddits[random_index]

def get_top_n_json(subreddit, n, time_frame):
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
    
    # combine data
    posts = []
    for i in range(len(titles)): # use length of titles because not gaurunteed to return up to limit
        posts.append({'title': titles[i], 'img_url': image_urls[i]})

    return posts
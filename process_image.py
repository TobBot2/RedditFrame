import math
import requests
# import bs4
from PIL import Image

def save_image_to_file(url):
    raw_img = requests.get(url).content
    with open('cuteness.png', 'wb') as f:
        f.write(raw_img)

    # soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
    # img_url = soup.find_all('img')[0].get('src')
    # raw_img = requests.get(img_url).content
    # with open('cuteness.png', 'wb') as f:
    #     f.write(raw_img)

def resize_and_crop(new_size):
    # TODO size to fit width or height (whatever is smaller) to new_size, then crop the other to be also new_size while keeping the image centered
    with Image.open('cuteness.png') as img:
        size = img.size
        aspect = size[1] / size[0] # y/x
        new_aspect = new_size[1] / new_size[0]
        if aspect > new_aspect:
            # crop vertically
            source_box = (0, size[1]/2 - size[0]/2, size[0], size[0] * aspect / new_aspect)
        else:
            # crop horizontally
            source_box = (size[0]/2 - size[1]/2, 0, size[1] * aspect / new_aspect, size[1])
        new_img = img.resize((new_size[0], new_size[1]), Image.BILINEAR, source_box)
        new_img.save('cuteness.png')
    

def FS_dithering():
    # Floyd-Steinberg Dithering Algorithm
    # https://github.com/CodingTrain/website/blob/main/CodingChallenges/CC_090_dithering/Processing/CC_090_dithering/CC_090_dithering.pde
    factor = 1 # binary - black or white. pretty much - idk why not (maybe because of x/16.0?)

    with Image.open('cuteness.png') as img:
        pixels = img.load()

        # TODO auto-expose. scale so max brightness is 1, min is 0 (for gray_pixel)
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                (r, g, b) = pixels[x, y]
                gray_pixel = int(math.sqrt(r*r + g*g + b*b))
                quantized_pixel = int(round(factor * gray_pixel / 255) * (255/factor))

                pixels[x, y] = quantized_pixel

                diff = gray_pixel - quantized_pixel

                # do stuff for pixel to the right
                neighbor_pixel = pixels[x+1, y][0]
                new_neighbor_pixel = int(neighbor_pixel + diff * 7/16.0)
                pixels[x+1, y] = (new_neighbor_pixel, new_neighbor_pixel, new_neighbor_pixel)

                # now bottom left
                neighbor_pixel = pixels[x-1, y+1][0]
                new_neighbor_pixel = int(neighbor_pixel + diff * 3/16.0)
                pixels[x-1, y+1] = (new_neighbor_pixel, new_neighbor_pixel, new_neighbor_pixel)

                # now bottom
                neighbor_pixel = pixels[x, y+1][0]
                new_neighbor_pixel = int(neighbor_pixel + diff * 5/16.0)
                pixels[x, y+1] = (new_neighbor_pixel, new_neighbor_pixel, new_neighbor_pixel)

                #now bottom right
                neighbor_pixel = pixels[x+1, y+1][0]
                new_neighbor_pixel = int(neighbor_pixel + diff * 1/16.0)
                pixels[x+1, y+1] = (new_neighbor_pixel, new_neighbor_pixel, new_neighbor_pixel)

        img.save('cuteness.png')
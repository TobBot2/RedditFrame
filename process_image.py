import math
import requests
# import bs4
from PIL import Image, ImageOps

def save_image_to_file(url):
    raw_img = requests.get(url).content
    with open('cuteness.png', 'wb') as f:
        f.write(raw_img)

def resize_and_crop(new_size):
    with Image.open('cuteness.png') as img:
        size = img.size
        aspect = size[0] / size[1] # x/y
        new_aspect = new_size[0] / new_size[1]
        if aspect < new_aspect:
            # crop vertically
            crop_h = size[0] / new_aspect
            source_box = (0, size[1]/2 - crop_h/2, size[0], size[1]/2 + crop_h/2)
        else:
            # crop horizontally
            crop_w = size[1] * new_aspect
            source_box = (size[0]/2 - crop_w/2, 0, size[0]/2 + crop_w/2, size[1])

        new_img = img.resize((new_size[0], new_size[1]), Image.BILINEAR, source_box)
        new_img.save('cuteness.png')

def resize_with_bars(new_size):
    with Image.open('cuteness.png') as img:
        size = img.size
        aspect = size[0] / size[1]
        new_aspect = new_size[0] / new_size[1]
        if (aspect > new_aspect): # increasing size, so flip the check
            # expand vertically
            border = int((size[0] - size[1] * new_aspect) /2)
            img = ImageOps.expand(img, (0, border), (0, 0, 0))
        else:
            # expand horizontally
            border = int((size[1] - size[0] / new_aspect) /2)
            img = ImageOps.expand(img, (border, 0), (0, 0, 0))
        img = img.resize(new_size, Image.BILINEAR)
        img.save('cuteness.png')

def FS_dithering():
    # Floyd-Steinberg Dithering Algorithm
    # https://github.com/CodingTrain/website/blob/main/CodingChallenges/CC_090_dithering/Processing/CC_090_dithering/CC_090_dithering.pde
    factor = 1 # binary - black or white. pretty much - idk why not (maybe because of x/16.0?)
    brightness_deviation = .02 # [0, .5), .02 is good

    with Image.open('cuteness.png') as img:
        pixels = img.load()

        # gray scale the image and get darkest value
        brightnesses = [] # brightness values for each pixel
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                (r, g, b) = pixels[x, y]
                pixel_brightness = (r + g + b) / 3
                if (pixel_brightness != 0): brightnesses.append(pixel_brightness) # don't include pitch black
                pixels[x, y] = (int(pixel_brightness), int(pixel_brightness), int(pixel_brightness))

        # TODO set the map range of the pixels based on 'brightnesses' mean, median and/or mode
        brightnesses.sort()
        brightestish = brightnesses[int(len(brightnesses) * (1 - brightness_deviation)) - 1]
        darkestish = brightnesses[int(len(brightnesses) * brightness_deviation)]
        brightness_scale = 255 / (brightestish - darkestish)
        
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                (r, g, b) = pixels[x, y]
                gray_pixel = int((r - darkestish) * brightness_scale + darkestish) # only use r because it is already gray-scale
                if gray_pixel > 255: gray_pixel = 255 # constrain
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
       
        # make completely black and white
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                (r, g, b) = pixels[x, y] # only use red value because they are all the same
                quantized_pixel = int(round(r / 255) * 255)
                pixels[x, y] = (quantized_pixel, quantized_pixel, quantized_pixel)

        img.save('cuteness.png')
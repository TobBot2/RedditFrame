import filer

import requests
from PIL import Image, ImageOps

def get_image_from_url(url: str):
    raw_img = requests.get(url).content
    with open(filer.base() + 'postimg.png', 'wb') as f:
        f.write(raw_img)

def resize_and_crop(new_size: tuple[int, int]):
    with Image.open(filer.base() + 'postimg.png') as img:
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
        new_img.save(filer.base() + 'postimg.png')

def resize_with_bars(new_size: tuple[int, int]):
    bar_color = (128, 128, 128)

    with Image.open(filer.base() + 'postimg.png') as img:
        size = img.size
        aspect = size[0] / size[1]
        new_aspect = new_size[0] / new_size[1]
        if (aspect > new_aspect): # increasing size, so flip the check
            # expand vertically
            border = int((size[0] - size[1] * new_aspect) /2)
            vertical = True
            img = ImageOps.expand(img, (0, border), bar_color)
        else:
            # expand horizontally
            border = int((size[1] - size[0] / new_aspect) /2)
            vertical = False
            img = ImageOps.expand(img, (border, 0), bar_color)
        img = img.resize(new_size, Image.BILINEAR)
        img.save(filer.base() + 'postimg.png')

        # TODO: Fix corrected_border - only does left side for horizontal
        if vertical:
            corrected_border = border / (size[0] * new_aspect) * new_size[1]
        else:
            corrected_border = border / (size[1] / new_aspect) * new_size[0]

        # is_reject is determined if the aspect ratio is too far apart
        is_reject = False
        if (abs(aspect - new_aspect) > 1):
            is_reject = True

        # return bar info so I can reapply after the image processing (possibly) ruins it
        # also return whether it is a reject (based on difference in aspect ratio)
        return corrected_border, vertical, is_reject
    
def reapply_bars(bar_size: int, is_vertical: bool):
    # bar_size gets applied to top AND bottom, so don't multiply by 2!
    bar_color = (0, 0, 0)

    with Image.open(filer.base() + 'postimg.png') as img:
        pixels = img.load()
        if is_vertical:
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    if y < bar_size or y > img.size[1] - bar_size:
                        pixels[x, y] = bar_color
        else:
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    if x < bar_size or x > img.size[1] - bar_size:
                        pixels[x, y] = bar_color

        img.save(filer.base() + 'postimg.png')

def FS_dithering(filepath: str = "postimg.png"):
    # Floyd-Steinberg Dithering Algorithm
    # https://github.com/CodingTrain/website/blob/main/CodingChallenges/CC_090_dithering/Processing/CC_090_dithering/CC_090_dithering.pde
    factor = 1 # binary - black or white. pretty much - idk why not (maybe because of x/16.0?)
    brightness_deviation = .02 # [0, .5), .02 is good

    with Image.open(filer.base() + filepath) as img:
        pixels = img.load()

        # gray scale the image and store brightness values of each pixel
        brightnesses = []
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                #(r, g, b) = pixels[x, y]
                #pixel_brightness = (r + g + b) / 3
                pixel_brightness = (pixels[x, y][0] + pixels[x, y][1] + pixels[x, y][2]) / 3
                brightnesses.append(pixel_brightness)
                pixels[x, y] = (int(pixel_brightness), int(pixel_brightness), int(pixel_brightness))

        # scales brightness so it uses the full range of color for the most contrast
        brightnesses.sort()
        brightestish = brightnesses[int(len(brightnesses) * (1 - brightness_deviation)) - 1]
        darkestish = brightnesses[int(len(brightnesses) * brightness_deviation)]
        brightness_scale = 255 / (brightestish - darkestish)
        
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                #(r, g, b) = pixels[x, y]
                #gray_pixel = int((r - darkestish) * brightness_scale + darkestish) # only use r because it is already gray-scale
                gray_pixel = int((pixels[x, y][0] - darkestish) * brightness_scale + darkestish)
                if gray_pixel > 255: gray_pixel = 255 # constrain
                quantized_pixel = int(round(factor * gray_pixel / 255) * (255/factor))

                pixels[x, y] = (quantized_pixel, quantized_pixel, quantized_pixel)

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
        
        # make completely black and white (remove gray pixels that sometimes appear by accident)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                #(r, g, b) = pixels[x, y] # only use red value because they are all the same
                quantized_pixel = int(round(pixels[x, y][0] / 255) * 255)
                pixels[x, y] = (quantized_pixel, quantized_pixel, quantized_pixel)

        img.save(filer.base() + filepath)

def overlay_image(overlay_img_path: str, position: tuple[int, int]):
    with Image.open(filer.base() + overlay_img_path) as overlay_img:
        overlay_pixels = overlay_img.load()
    
    with Image.open(filer.base() + 'postimg.png') as img:
        pixels = img.load()
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if (x >= position[0] and y >= position[1] and
                    x  - position[0] < overlay_img.size[0] and y - position[1] < overlay_img.size[1]):
                    pixels[x, y] = overlay_pixels[x - position[0], y - position[1]]

        img.save(filer.base() + 'postimg.png')
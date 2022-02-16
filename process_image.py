import requests
import io
from PIL import Image, ImageOps

# TODO remove all references to 'cuteness.png' and just pass around the image as a variable

def get_image_from_url(url: str):
    raw_img = requests.get(url).content
    with open('cuteness.png', 'wb') as f:
        f.write(raw_img)
    img = Image.open('cuteness.png')
    return img

def resize_and_crop(img: Image.Image, new_size: tuple[int, int]):
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
    return new_img

def resize_with_bars(img: Image.Image, new_size: tuple[int, int]):
    bar_color = (128, 128, 128)

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
    # img.save('cuteness.png')

    # is_reject is determined if the aspect ratio is too far apart
    is_reject = False
    if (abs(aspect - new_aspect) > 1):
        is_reject = True

    
    # return bar info so I can reapply after the image processing (possibly) ruins it
    # also return whether it is a reject (based on difference in aspect ratio)
    return img, border, vertical, is_reject
    
def reapply_bars(img: Image.Image, bar_size: int, is_vertical: bool):
    # bar_size gets applied to top AND bottom, so don't multiply by 2!
    bar_color = (0, 0, 0)

    pixels = img.load()
    if is_vertical:
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if y < bar_size or y > img.size[1] - bar_size:
                    pixels[x, y] = bar_color
    if not is_vertical:
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if x < bar_size or x > img.size[1] - bar_size:
                    pixels[x, y] = bar_color

    return img

def FS_dithering(img_3: Image.Image):
    # Floyd-Steinberg Dithering Algorithm
    # https://github.com/CodingTrain/website/blob/main/CodingChallenges/CC_090_dithering/Processing/CC_090_dithering/CC_090_dithering.pde
    factor = 1 # binary - black or white. pretty much - idk why not (maybe because of x/16.0?)
    brightness_deviation = .02 # [0, .5), .02 is good

    with Image.open('cuteness.png') as img:
        pixels = img.load()

        # gray scale the image and store brightness values of each pixel
        brightnesses = []
        for x in range(img.size[0] - 1):
            for y in range(img.size[1] - 1):
                (r, g, b) = pixels[x, y]
                pixel_brightness = (r + g + b) / 3
                brightnesses.append(pixel_brightness)
                pixels[x, y] = (int(pixel_brightness), int(pixel_brightness), int(pixel_brightness))

        # scales brightness so it uses the full range of color for the most contrast
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
        
        # make completely black and white (remove gray pixels that sometimes appear by accident)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                (r, g, b) = pixels[x, y] # only use red value because they are all the same
                quantized_pixel = int(round(r / 255) * 255)
                pixels[x, y] = (quantized_pixel, quantized_pixel, quantized_pixel)

        return img

def overlay_image(base_img: Image.Image, overlay_img: Image.Image, position: tuple[int, int]):
    overlay_pixels = overlay_img.load()
    
    pixels = base_img.load()
    for x in range(base_img.size[0]):
        for y in range(base_img.size[1]):
            if (x >= position[0] and y >= position[1] and
                x  - position[0] < overlay_img.size[0] and y - position[1] < overlay_img.size[1]):
                pixels[x, y] = overlay_pixels[x - position[0], y - position[1]]

    return base_img
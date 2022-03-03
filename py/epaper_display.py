import filer
import process_image
import epd7in5_V2

from PIL import Image

def display_vertical():
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()

    # postimg.png is assumed to be proper size
    with Image.open(filer.base() + 'postimg.png') as img:
        epd.display(epd.getbuffer(process_image.format_for_epaper(img)))

    epd.sleep()
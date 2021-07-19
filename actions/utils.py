from PIL import Image
from io import BytesIO

def generate_gif(im1, im2):
    im1 = im1.resize((round(im1.size[0]*1), round(im1.size[1]*1)))
    im2 = im2.resize((round(im1.size[0]), round(im1.size[1])))

    images = []
    frames = 10

    for i in range(frames+1):
        im = Image.blend(im1, im2, i/frames)
        images.append(im)
        
    for i in range(frames+1):
        im = Image.blend(im1, im2, 1-i/frames)
        images.append(im)


    bio = BytesIO()
    bio.name = 'image.gif'

    images[0].save(bio, 'GIF', save_all=True, append_images=images[1:], duration=150, loop=0, optimize=True)
    bio.seek(0)
    return bio

def overlay_images(background, foreground):
    foreground = foreground.resize((round(background.size[0]), round(background.size[1])))
    background.paste(foreground, (0, 0), foreground)
    bio = BytesIO()
    bio.name = 'image.png'
    background.save(bio, 'PNG')
    bio.seek(0)
    return bio

from functools import wraps

def log(logger):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            if context.user_data["daten"]:
                logger.info(update)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

import re
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251" 
    "]+"
)
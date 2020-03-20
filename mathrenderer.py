from pathlib import Path
from io import BytesIO
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
import subprocess
import os

matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

# https://stackoverflow.com/a/31371907/7669319
def render_latex(filename, formula, fontsize=36, dpi=300, format_='jpg'):
    """Renders LaTeX formula into image.
    """
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, u'${}$'.format(formula), fontsize=fontsize)
    fig.savefig(filename, dpi=dpi, transparent=True, format=format_, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)



def resize(name, webp_name = None):
    """Resize image to Telegram's specified 512x512 pixels
    Uses cwebp for conversion (see https://www.tecmint.com/convert-images-to-webp-format-in-linux/)"""
    max_size = (512, 512)

    try:
        im = Image.open(name)
        im.thumbnail(max_size, Image.ANTIALIAS)
        im.save(name, "png")

        if webp_name is not None:
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(
                    ["cwebp", "-q", "60", name, "-o", webp_name]
                    , stdout=devnull, stderr=devnull)

    except IOError as e:
        print("Couldn't create small image")
        raise(e)

if __name__ == '__main__':
    render_latex('file.jpg',
        r'a = \bigl( \begin{smallmatrix}1 & 1\\ 0 & 1\end{smallmatrix}\bigr)',
        fontsize=10, dpi=200, format_='png')

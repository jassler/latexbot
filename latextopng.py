# DEPRECATED
# View mathrenderer.py for current implementation.
# This is kept here, because I liked the prospect of generating pngs from latex files.

import os
from pathlib import Path
from PIL import Image
import shutil
import subprocess
import tempfile

from IPython.lib.latextools import genelatex

# Much help gotten from here
# https://gist.github.com/rossant/b9a37747d37140105299b4564fafade1
def latex_to_image(latex, imgpath):
    """Turn latex source code into png image"""

    # tempfile stuff for tex-compiling
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = os.path.join(tmpdir, "tmp.tex")
        dvifile = os.path.join(tmpdir, "tmp.dvi")
        pngfile = os.path.join(tmpdir, "tmp.png")

        contents = list(genelatex(latex, False))
        with open(tmpfile, "w") as f:
            f.writelines(contents)

        with open(os.devnull, 'w') as devnull:
            try:
                subprocess.check_call(
                    ["latex", "-halt-on-error", tmpfile], cwd=tmpdir,
                    stdout=devnull, stderr=devnull)
            except Exception:
                print("************")
                print(len(contents))
                print('\n'.join(contents))
                return False

            # create png
            subprocess.check_call(
                ["dvipng", "-T", "tight", "-x", "6000", "-z", "9",
                 "-bg", "transparent", "-o", pngfile, dvifile], cwd=tmpdir,
                stdout=devnull, stderr=devnull)

        # copy png from temp folder to current folder
        shutil.copy(pngfile, Path(imgpath).with_suffix('.png'))
        return True


def resize(name, to_webp = False):
    """Resize image to Telegram's specified 512x512 pixels
    Uses cwebp for conversion (see https://www.tecmint.com/convert-images-to-webp-format-in-linux/)"""
    max_size = (512, 512)

    try:
        im = Image.open(name)
        im.thumbnail(max_size, Image.ANTIALIAS)
        im.save(name, "png")

        if to_webp:
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(
                    ["cwebp", "-q", "60", name, "-o", Path(name).with_suffix(".webp")]
                    , stdout=devnull, stderr=devnull)

    except IOError as e:
        print("Couldn't create small image")
        raise(e)

if __name__ == '__main__':
    latex_to_image(r'$\frac{1}{3} = a \cdot b$',
                   'calc.png')
    resize('calc.png')

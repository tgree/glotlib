import os

from .font import Face


vera = None


def load():
    global vera

    vera = Face(os.path.join('ttf-bitstream-vera-1.10', 'Vera.ttf'))

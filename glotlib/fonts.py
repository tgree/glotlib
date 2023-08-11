from .font import Face


vera = None


def load():
    global vera

    vera = Face('ttf_bitstream_vera_1_10', 'Vera.ttf')

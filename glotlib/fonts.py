from .font import Face


vera = None
vera_bold = None


def load():
    global vera
    global vera_bold

    vera = Face('ttf_bitstream_vera_1_10', 'Vera.ttf')
    vera_bold = Face('ttf_bitstream_vera_1_10', 'VeraBd.ttf')

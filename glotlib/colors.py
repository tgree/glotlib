tab10 = [
    (0x1F / 0xFF, 0x77 / 0xFF, 0xB4 / 0xFF, 1),
    (0xFF / 0xFF, 0x7F / 0xFF, 0x0E / 0xFF, 1),
    (0x2C / 0xFF, 0xA0 / 0xFF, 0x2C / 0xFF, 1),
    (0xD6 / 0xFF, 0x27 / 0xFF, 0x28 / 0xFF, 1),
    (0x94 / 0xFF, 0x67 / 0xFF, 0xBD / 0xFF, 1),
    (0x8C / 0xFF, 0x56 / 0xFF, 0x4B / 0xFF, 1),
    (0xE3 / 0xFF, 0x77 / 0xFF, 0xC2 / 0xFF, 1),
    (0x7F / 0xFF, 0x7F / 0xFF, 0x7F / 0xFF, 1),
    (0xBC / 0xFF, 0xBD / 0xFF, 0x22 / 0xFF, 1),
    (0x17 / 0xFF, 0xBE / 0xFF, 0xCF / 0xFF, 1),
]

named_colors = {
    'red'       : (1, 0, 0, 1),
    'green'     : (0, 1, 0, 1),
    'blue'      : (0, 0, 1, 1),
    'black'     : (0, 0, 0, 1),
    'white'     : (1, 1, 1, 1),
}


def cycle(iterable):
    while iterable:
        for e in iterable:
            yield e


def make(v, none_iter):
    if v is None:
        return next(none_iter)
    if isinstance(v, tuple):
        if len(v) == 4:
            return v
        if len(v) == 3:
            return (v[0], v[1], v[2], 1)
    if isinstance(v, str):
        if v.startswith('#'):
            r = int(v[1:3], 16)
            g = int(v[3:5], 16)
            b = int(v[5:7], 16)
            return (r / 0xFF, g / 0xFF, b / 0xFF, 1)
        return named_colors[v]

    raise Exception('Cannot convert %s to a color.' % (v,))

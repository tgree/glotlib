from . import fonts


FONTS_INITED    = False


def init_fonts():
    global FONTS_INITED

    if FONTS_INITED:
        return

    fonts.load()
    FONTS_INITED = True

import importlib.resources
import sys
import os

import numpy as np
import freetype

from OpenGL import GL


def is_pow2(v):
    '''
    Returns true if v is a power of 2.
    '''
    return (v != 0) and ((v & (v - 1)) == 0)


def ceil_pow2(v):
    '''
    Return v rounded up to the nearest power of 2.  Returns v if it is already a
    power of 2.  Works for numbers up to 65536.
    '''
    v -= 1
    v |= (v >> 1)
    v |= (v >> 2)
    v |= (v >> 4)
    v |= (v >> 8)
    return v + 1


assert ceil_pow2(1) == 1
assert ceil_pow2(2) == 2
assert ceil_pow2(3) == 4
assert ceil_pow2(4) == 4
assert ceil_pow2(5) == 8
assert ceil_pow2(10) == 16
assert ceil_pow2(123) == 128
assert ceil_pow2(2000) == 2048
assert ceil_pow2(60000) == 65536


def round_up_pow2(v, K):
    '''
    Round up to the nearest multiple of K, which must be a power of 2.
    '''
    return (v + K - 1) & ~(K - 1)


assert round_up_pow2(5,   8)  == 8
assert round_up_pow2(20,  8)  == 24
assert round_up_pow2(121, 32) == 128
assert round_up_pow2(2,   32) == 32


class Glyph:
    def __init__(self, bm_left, bm_top, bm_width, bm_height, dx, tex_x0,
                 tex_y0, tex_x1, tex_y1):
        self.bm_left   = bm_left
        self.bm_top    = bm_top
        self.bm_width  = bm_width
        self.bm_height = bm_height
        self.dx        = dx
        self.tex_x0    = tex_x0
        self.tex_y0    = tex_y1
        self.tex_x1    = tex_x1
        self.tex_y1    = tex_y0
        self.tex_coords = [
            (self.tex_x0, self.tex_y0),
            (self.tex_x1, self.tex_y1),
            (self.tex_x0, self.tex_y1),
            (self.tex_x0, self.tex_y0),
            (self.tex_x1, self.tex_y0),
            (self.tex_x1, self.tex_y1),
        ]


class Font:
    def __init__(self, tex_data, glyphs, oversample_log2, ascender, height):
        self.tex_data   = tex_data
        self.tex_w      = tex_data.shape[1]
        self.tex_h      = tex_data.shape[0]
        self.glyphs     = glyphs
        self.oversample = (1 << oversample_log2)
        self.ascender   = ascender
        self.height     = height
        self.tex        = GL.glGenTextures(1)
        self.bind_unit  = None

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                           GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                           GL.GL_NEAREST)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_R8, tex_data.shape[1],
                        tex_data.shape[0], 0, GL.GL_RED, GL.GL_UNSIGNED_BYTE,
                        tex_data)

    def bind(self, unit):
        GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex)
        self.bind_unit = unit

    def gen_vertices_left(self, text, dy=1):
        '''
        Generates vertices for left-aligned text, returning a tuple:

            (window vertices, texture coords, window width, window height)

        For text to grow downwards, set dy = -1.  For text to grow upwards, set
        dy = 1.
        '''
        pen_x      = 0
        pen_y      = 0
        width      = 0
        vertices   = []
        tex_coords = []
        for c in text:
            if c == '\n':
                width  = max(width, pen_x)
                pen_x  = 0
                pen_y += dy * (self.height // (64 * self.oversample))
                continue

            g = self.glyphs[c]
            w = g.bm_width / self.oversample
            h = g.bm_height / self.oversample
            if w or h:
                x = pen_x + g.bm_left / self.oversample
                y = pen_y + g.bm_top / self.oversample - h
                vertices += [(x, y),
                             (x + w, y + h),
                             (x, y + h),
                             (x, y),
                             (x + w, y),
                             (x + w, y + h),
                             ]
                tex_coords += g.tex_coords

            pen_x += g.dx / self.oversample

        width      = max(width, pen_x)
        vertices   = np.array(vertices, dtype=np.float32)
        tex_coords = np.array(tex_coords, dtype=np.float32)

        return vertices, tex_coords, width, pen_y + self.ascender


class Face:
    def __init__(self, family, name):
        if sys.version_info < (3, 9):
            with importlib.resources.open_binary(
                    'glotlib.font_files.%s' % family, name) as byte_stream:
                self.face = freetype.Face(byte_stream)
        else:
            name  = os.path.join(family, name)
            files = importlib.resources.files('glotlib.font_files')
            with files.joinpath(name).open('rb') as byte_stream:
                self.face = freetype.Face(byte_stream)

        self.sizes = {}

    def __call__(self, size, oversample_log2=0):
        font = self.sizes.get((size, oversample_log2))
        if font is None:
            font = self._load_size(size, oversample_log2)
        self.sizes[(size, oversample_log2)] = font
        return font

    def _load_size(self, size, oversample_log2):
        self.face.set_char_size(int(size * 64 * (1 << oversample_log2)))

        rows  = 1
        x     = 0
        row_h = 0
        tex_h = 0
        asc   = 0
        for _, ci in self.face.get_chars():
            self.face.load_glyph(ci)
            g  = self.face.glyph
            w  = g.bitmap.width
            x += w
            if x > 1024:
                rows  += 1
                x      = w
                tex_h += row_h
                row_h  = 0

            row_h = max(row_h, g.bitmap.rows)
            asc   = max(asc, g.bitmap_top / (1 << oversample_log2))

        tex_h    = ceil_pow2(tex_h + row_h)
        tex_w    = 1024 if rows > 1 else ceil_pow2(x)
        tex_data = np.zeros((tex_h, tex_w), dtype=np.ubyte)

        x     = 0
        y     = 0
        row_h = 0
        do    = oversample_log2 / 2
        glyphs = {}
        for cc, ci in self.face.get_chars():
            c = chr(cc)
            self.face.load_glyph(ci)
            g = self.face.glyph

            w = g.bitmap.width
            if x + w >= 1024:
                x     = 0
                y    += row_h
                row_h = 0
            row_h = max(row_h, g.bitmap.rows)

            tex_x = x
            tex_y = y
            tex_data[tex_y:tex_y + g.bitmap.rows,
                     tex_x:tex_x + g.bitmap.width].flat = g.bitmap.buffer

            glyphs[c] = Glyph(g.bitmap_left, g.bitmap_top, w, g.bitmap.rows,
                              g.advance.x >> 6,
                              (x + do) / tex_w, (y + do) / tex_h,
                              (x + w - do) / tex_w,
                              (y + g.bitmap.rows - do) / tex_h)

            x += w

        return Font(tex_data, glyphs, oversample_log2, asc,
                    self.face.size.height)

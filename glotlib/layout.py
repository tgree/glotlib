def _bounds_hwp(h, w, p):
    p -= 1
    y  = h - (p // w) - 1
    x  = p % w

    return (x / w, y / h, (x + 1) / w, (y + 1) / h)


def _bounds_hwr(h, w, r):
    b0 = _bounds_hwp(h, w, r[0])
    b1 = _bounds_hwp(h, w, r[1])
    return (min(b0[0], b1[0]), min(b0[1], b1[1]),
            max(b0[2], b1[2]), max(b0[3], b1[3]))


def _bounds_int(b):
    assert 111 <= b <= 999
    h = b // 100
    w = (b % 100) // 10
    p = (b % 10)
    return _bounds_hwp(h, w, p)


def parse_bounds(b):
    '''
    Parse a bounds specifier into an (l, b, r, t) bounds tuple, where the
    elements of the tuple are percentages of the enclosing bounds.  The
    bounds specifier either describes a grid of equal-sized cells and a
    minimal rectangle enclosing a subset of those cells, or it specifies the
    percentages directly as a 4-tuple.

    In the case where a grid and cells are specified, the grid is
    conceptualized as having a height h and width w, and cells numbered as
    follows (example for a 4-wide by 3-high grid):

        1, 2,  3,  4,
        5, 6,  7,  8,
        9, 10, 11, 12

    Note that the first cell is numbered 1 and cell numbers are referred to as
    "p" in the descriptions below.

    In the case where a grid and cells are specified, the parameter b can take
    on one of the following forms:

        3-tuple (h, w, p)
        =================
        Interpret the value h as the height of the grid, the value w as the
        width of the grid and the value p as the cell in the grid for which to
        compute the bounds.

        Integer between 111-999
        =======================
        Given the value b, in the range 111 to 999, interpret the value as
        though the first digit were the height of the grid, the second digit
        were the width of the grid and the third digit was the position p in
        the grid, and then compute the coordinates as though (h, w, p) were
        passed in as b.

        3-tuple (h, w, (p0, p1))
        ========================
        Given a grid of height h and width w, and a tuple (p0, p1), returns
        the bounds (l, b, r, t) of the smallest rectangle fully enclosing both
        p0 and p1, with coordinates as percentages of the total grid.  In the
        example grid above, the range (2, 7) and (7, 2) would both specify the
        same rectangle, covering cells 2, 3, 6 and 7.

    Raises an exception if the bounds cannot be parsed or are invalid.
    '''
    if isinstance(b, int):
        return _bounds_int(b)
    if isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], int):
        return _bounds_hwp(*b)
    if isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], tuple):
        return _bounds_hwr(*b)
    if isinstance(b, tuple) and len(b) == 4:
        return b

    raise Exception('Cannot handle bounds %s' % (b,))

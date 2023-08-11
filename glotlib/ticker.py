import math


R    = (1., 2., 5., 2.5)
DLOG = (0, 0, 0, 1)


def gen_ticks_dx(w, Nmin, Nmax):
    w_log        = math.log(w, 10)
    Nmin_log     = math.log(Nmin - 1, 10)
    Nmax_log     = math.log(Nmax, 10)
    best, best_K = None, 0

    for r, dlog in zip(R, DLOG):
        q    = w_log - math.log(r, 10)
        Kmin = q - Nmax_log
        Kmax = q - Nmin_log
        K    = math.floor(Kmax)
        # print('%f: %f %f' % (r, Kmin, Kmax))
        if math.ceil(Kmin) <= K < Kmax:
            dx = r * 10**K
            if best is None or dx < best:
                best, best_K = dx, K - dlog

    return best, -best_K


def gen_ticks(l, r, Nmin=2, Nmax=5):
    '''
    Generates a list of numbers that should be used as tick coordinates.
    Returns a tuple:

        [tick1, tick2, ..., tickN], K

    where K is the number of decimal points that should be displayed.
    '''
    w  = l - r

    if w == 0:
        a, K = [l], 10
    else:
        dx, K = gen_ticks_dx(r - l, Nmin, Nmax)
        i_min = math.floor(l / dx)
        i_max = math.ceil(r / dx)
        a = [i * dx for i in range(i_min, i_max + 1) if l <= i * dx <= r]

    # print('(%.10f, %.10f): %u %s' % (l, r, K, a))
    return a, K


def _text_for_val(v, K):
    if v == 0:
        return '0'

    K      = max(K, 0)
    digits = math.floor(math.log10(abs(v))) + K + 1
    text   = '%#.*g' % (digits, v)
    if text[-1] == '.':
        return text[:-1]
    return text


def gen_ticks_and_texts(*args, **kwargs):
    '''
    Generates a pair of lists that include the tick coordinates as numbers and
    as formatted text for display.
    '''
    ticks, K = gen_ticks(*args, **kwargs)
    texts    = [_text_for_val(t, K) for t in ticks]
    return ticks, texts


assert _text_for_val(32700, -2) == '32700'
assert _text_for_val(32700, -1) == '32700'
assert _text_for_val(32700,  0) == '32700'
assert _text_for_val(32700,  1) == '32700.0'
assert _text_for_val(1000, -2) == '1000'
assert _text_for_val(0.0001, 5) == '0.00010'
assert _text_for_val(0.00001, 6) == '1.0e-05'
assert _text_for_val(0.00001, 7) == '1.00e-05'

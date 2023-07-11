import math

import numpy as np

import glotlib


NVERTICES = 501
RATIO     = 0.2


def tukey_window(N, R):
    '''
    Generates a Tukey window of length N.  The fraction R specifies how much of
    the window is taken up in total by the ramp-up and ramp-down.  The window
    is laid out as:

        (R / 2) * N - this many samples are in the ramp-up phase
        (1 - R) * N - this many samples are in the ones phase
        (R / 2) * N - this many samples are in the ramp-down phase

    So, a fraction of R/2 is used on either end of the window and the fraction
    (1 - R) is left over for the all-ones middle part.
    '''
    window = np.ones(N)
    sin_ts = np.linspace(-math.pi / 2, math.pi / 2, round((R / 2) * N))
    window[:len(sin_ts)]  = 0.5 * (np.sin(sin_ts) + 1)
    window[-len(sin_ts):] = window[len(sin_ts) - 1::-1]
    return window


w = glotlib.Window(900, 650, msaa=4)
p = w.add_plot(limits=(0, 0, NVERTICES - 1, 1))
X = np.arange(NVERTICES)
Y = tukey_window(NVERTICES, RATIO)
p.add_lines(X=X, Y=Y)

glotlib.interact()

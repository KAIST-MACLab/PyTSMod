import numpy as np


def win(win_type='hann', win_size=4096, zero_pad=0):
    """Generate diverse type of window function

    Parameters
    ----------

    win_type : str
               the type of window function.
               Currently, Hann and Sin are supported.
    win_size : int > 0 [scalar]
               the size of window function.
               It doesn't contains the length of zero padding.
    zero_pad : int > 0 [scalar]
               the total length of zero-pad.
               Zeros are equally distributed
               for both left and right of the window.

    Returns
    -------

    win : numpy.ndarray([shape=(win_size)])
          the window function generated.
    """

    if win_type == 'hann':
        win = np.hanning(win_size)
    elif win_type == 'sin':
        win = np.sin(np.pi * np.arange(win_size) / (win_size - 1))
    else:
        raise Exception("Please use the valid window type. (hann, sin)")

    win = np.pad(win, zero_pad // 2, 'constant')

    return win

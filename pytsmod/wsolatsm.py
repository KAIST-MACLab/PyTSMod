import numpy as np
from scipy.interpolate import interp1d
from .utils import win as win_func
from .utils import _validate_audio, _validate_scale_factor


def wsola(x, s, win_type='hann',
          win_size=1024, syn_hop_size=512, tolerance=512):
    """Modify length of the audio sequence using WSOLA algorithm.

    Parameters
    ----------

    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to modify.
    s : number > 0 [scalar] or numpy.ndarray [shape=(2, num_points)]
        the time stretching factor. Either a constant value (alpha)
        or an 2 x n array of anchor points which contains the sample points
        of the input signal in the first row
        and the sample points of the output signal in the second row.
    win_type : str
               type of the window function. hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    syn_hop_size : int > 0 [scalar]
                   hop size of the synthesis window.
                   Usually half of the window size.
    tolerance : int >= 0 [scalar]
                number of samples the window positions
                in the input signal may be shifted
                to avoid phase discontinuities when overlap-adding them
                to form the output signal (given in samples).

    Returns
    -------

    y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the modified output audio sequence.
    """
    # validate the input audio and scale factor.
    x = _validate_audio(x)
    anc_points = _validate_scale_factor(x, s)

    n_chan = x.shape[0]
    output_length = int(anc_points[-1, -1]) + 1

    win = win_func(win_type=win_type, win_size=win_size, zero_pad=0)

    sw_pos = np.arange(0, output_length + win_size // 2, syn_hop_size)
    ana_interpolated = interp1d(anc_points[1, :], anc_points[0, :],
                                fill_value='extrapolate')
    aw_pos = np.round(ana_interpolated(sw_pos)).astype(int)
    ana_hop = np.insert(aw_pos[1:] - aw_pos[0: -1], 0, 0)

    y = np.zeros((n_chan, output_length))

    min_fac = np.min(syn_hop_size / ana_hop[1:])

    # padding the input audio sequence.
    left_pad = int(win_size // 2 + tolerance)
    right_pad = int(np.ceil(1 / min_fac) * win_size + tolerance)
    x_padded = np.pad(x, ((0, 0), (left_pad, right_pad)), 'constant')

    aw_pos = aw_pos + tolerance

    # Applying WSOLA to each channels
    for c, x_chan in enumerate(x_padded):
        y_chan = np.zeros(output_length + 2 * win_size)
        ow = np.zeros(output_length + 2 * win_size)

        delta = 0

        for i in range(len(aw_pos) - 1):
            x_adj = x_chan[aw_pos[i] + delta: aw_pos[i] + win_size + delta]
            y_chan[sw_pos[i]: sw_pos[i] + win_size] += x_adj * win
            ow[sw_pos[i]: sw_pos[i] + win_size] += win

            nat_prog = x_chan[aw_pos[i] + delta + syn_hop_size:
                              aw_pos[i] + delta + syn_hop_size + win_size]

            next_aw_range = np.arange(aw_pos[i+1] - tolerance,
                                      aw_pos[i+1] + win_size + tolerance)

            x_next = x_chan[next_aw_range]

            cross_corr = np.correlate(nat_prog, x_next)
            max_index = np.argmax(cross_corr)

            delta = tolerance - max_index

        # Calculate last frame
        x_adj = x_chan[aw_pos[-1] + delta: aw_pos[-1] + win_size + delta]
        y_chan[sw_pos[-1]: sw_pos[-1] + win_size] += x_adj * win
        ow[sw_pos[-1]: sw_pos[-1] + win_size] += + win

        ow[ow < 1e-3] = 1

        y_chan = y_chan / ow
        y_chan = y_chan[win_size // 2:]
        y_chan = y_chan[: output_length]

        y[c, :] = y_chan

    return y.squeeze()

import numpy as np

from .utils import win as win_func


def tdpsola(x, sr, src_f0, tgt_f0=None, alpha=1, beta=None,
            win_type='hann', p_hop_size=441, p_win_size=1470):
    """Modify length and pitch of the audio sequnce using TD-PSOLA algorithm.

    Parameters
    ----------

    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to modify.
    sr : int > 0 [scalar]
         sample rate of the input audio sequence.
    src_f0 : numpy.ndarray [shape=(channel, num_freqs) or (num_freqs)]
             the fundamental frequency contour of the input audio sequence.
    tgt_f0 : numpy.ndarray [shape=(channel, num_freqs) or (num_freqs)]
              the target fundamental frequency contour
              you want to modify the input audio sequence.
              Should not be used with beta.
    alpha : number > 0 [scalar]
            time stretching factor.
    beta : number > 0 [scalar]
           the pitch shifting factor. should not be used with target_f0.
    win_type : str
               type of the window function. hann and sin are available.
    p_hop_size : int > 0 [scalar]
                the hop size of src_f0 (in samples).
    p_win_size : int > 0 [scalar]
                 the window size of pitch tracking algorithm
                 you used. (in samples).

    Returns
    -------

    y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the modified output audio sequence.
    """

    if x.ndim == 1:  # make mono source to 2D array with a single row.
        x = np.expand_dims(x, 0)
    elif x.ndim > 2:
        raise Exception("Please use the valid audio source. "
                        + "Number of dimension of input should be less than 3.")

    if src_f0.ndim == 1:
        src_f0 = np.expand_dims(src_f0, 0)
    elif src_f0.ndim == 2:
        if x.shape[0] != src_f0.shape[0] and src_f0.shape[0] != 1:
            raise Exception("The number of channels of source f0 value "
                            + "should 1 or same as the source.")
    elif src_f0.ndim > 2:
        raise Exception("Please use the valid source f0 value. "
                        + "Number of dimension of source f0 "
                        + "should be less than 3.")

    # Check if system uses target_f0 or beta.
    if (tgt_f0 is None) and beta is None:
        beta = 1
    elif beta is None:  # Uses target_f0
        if tgt_f0.ndim == 1:
            tgt_f0 = np.expand_dims(tgt_f0, 0)
        elif tgt_f0.ndim == 2:
            if x.shape[0] != tgt_f0.shape[0] and tgt_f0.shape[0] != 1:
                raise Exception("The number of channels of target f0 value "
                                + "should 1 or same as the source.")
        elif tgt_f0.ndim > 2:
            raise Exception("Please use the valid target f0 value. "
                            + "Number of dimension of target f0 "
                            + "should be less than 3.")
    elif (tgt_f0 is not None) and (beta is not None):
        raise Exception("You cannot use both target_f0 and beta as an input.")
    elif not np.isscalar(beta):
        raise Exception("The beta value should be a scalar.")

    n_channels = x.shape[0]
    output_length = int(np.ceil(x.shape[1] * alpha))
    y = np.zeros((n_channels, output_length))

    for c, x_chan in enumerate(x):
        if src_f0.ndim == 1:
            src_f0_chan = src_f0
        else:
            src_f0_chan = src_f0[c]

        src_f0_chan[np.isnan(src_f0_chan)] = 0
        pm_chan = _find_pitch_marks(x_chan, sr, src_f0_chan, p_hop_size,
                                    p_win_size)

        if tgt_f0 is not None:
            if tgt_f0.ndim == 1:
                tgt_f0_chan = tgt_f0
            else:
                tgt_f0_chan = tgt_f0[c]
            beta = _target_f0_to_beta(x_chan, pm_chan,
                                      src_f0_chan, tgt_f0_chan)

        pitch_period = np.diff(pm_chan)  # compute pitch periods

        # make beta to an array if beta is a fixed value.
        if np.isscalar(beta):
            beta = np.ones(pitch_period.size) * beta

        if pm_chan[0] <= pitch_period[0]:  # remove first pitch mark
            pm_chan = pm_chan[1:]
            pitch_period = pitch_period[1:]
            beta = beta[1:]

        if pm_chan[-1] + pitch_period[-1] > x_chan.size:  # remove last pitch mark
            pm_chan = pm_chan[: -1]
        else:
            pitch_period = np.append(pitch_period, pitch_period[-1])
            beta = np.append(beta, beta[-1])

        output_length = int(np.ceil(x.size * alpha))
        x_chan = np.pad(x_chan, (1024, 1024))
        y_chan = np.zeros(output_length + 2 * 1024)  # output signal

        tk = pitch_period[0] + 1  # output pitch mark
        ow = np.zeros(y_chan.shape)

        while np.round(tk) < output_length:
            i = min(np.argmin(np.abs(alpha * pm_chan - tk)),
                    pitch_period.size - 1)  # find analysis segment
            pit = pitch_period[i]

            win = win_func(win_type=win_type, win_size=2 * pit + 1)

            st = pm_chan[i] - pit
            en = pm_chan[i] + pit

            gr = x_chan[st + 1024: en + 1024 + 1] * win

            ini_gr = round(tk) - pit + 1024
            end_gr = round(tk) + pit + 1024

            y_chan[ini_gr: end_gr + 1] = y_chan[ini_gr: end_gr + 1] + gr
            ow[ini_gr: end_gr + 1] = ow[ini_gr: end_gr + 1] + win
            tk = tk + pit / beta[i]

        ow[ow < 1e-3] = 1

        y_chan = y_chan / ow
        y_chan = y_chan[1024:]
        y_chan = y_chan[: output_length]
        y[c, :] = y_chan

    return np.squeeze(y)


def _target_f0_to_beta(x, pitch_mark, source_f0, target_f0):
    """Modify target_f0 to continuous beta, a time-varying pitch-shifting rate.

    Parameters
    ----------

    x : numpy.ndarray [shape=(num_samples)]
        the input audio sequence to modify.
    pitch_mark : numpy.ndarray [shape=(num_pitch_marks]
         pitch_marks extracted from the input audio sequence.
    source_f0 : numpy.ndarray [shape=(num_freqs)]
                the fundamental frequency contour of the input audio sequence.
    target_f0 : numpy.ndarray [shape=(num_freqs)]
                 the target fundamental frequency contour
                 you want to modify the input audio sequence.
                 Should not be used with beta.

    Returns
    -------

    beta : numpy.ndarray [shape=(num_pitch_marks)]
           time-varying pitch-shifting rate.
    """
    beta = np.zeros(pitch_mark.size)
    for i in range(beta.size):
        idx = round(pitch_mark[i] * source_f0.size / x.size)
        if idx < 0:
            idx = 0
        elif idx >= source_f0.size:
            idx = source_f0.size - 1

        if (not target_f0[idx] == 0) and (not source_f0[idx] == 0):
            beta[i] = target_f0[idx] / source_f0[idx]
        else:
            beta[i] = 1

    return beta


def _find_pitch_marks(x, sr, f0, hop_size, win_size):
    """Find pitch marks for TD-PSOLA.

    Parameters
    ----------

    x : numpy.ndarray [shape=(num_samples)]
        the input audio sequence to find pitch marks.
    sr : int > 0 [scalar]
         sample rate of the input audio sequence.
    f0 : numpy.ndarray [shape=(num_freqs)]
         the fundamental frequency contour of the input audio sequence.
    p_hop_size : int > 0 [scalar]
               the hop size of f0 contour (in samples).
    p_win_size : int > 0 [scalar]
                   the window size of pitch tracking algorithm
                   you used. (in samples).

    Returns
    -------

    m : numpy.ndarray [shape=(num_pitch_marks)]
        pitch_marks extracted from the input audio sequence.
    """

    # Initialization
    m = np.array([0])  # vector of pitch mark positions

    # set pitch periods of unvoiced frames
    if f0[0] == 0:
        f0[0] = 120
    for i in range(f0.size):
        if f0[i] == 0:
            f0[i] = f0[i - 1]

    p0 = np.round(sr / f0)
    search_up_lim = int(p0[0])
    last_m = 0

    # processing frames i
    for i in range(f0.size):
        if i == 0:
            loc = np.argmax(x[: search_up_lim])
            local_m = np.array([loc])
        else:
            search_up_lim = search_up_lim + p0[i]
            local_m = np.array([last_m + p0[i]])

        while search_up_lim + p0[i] <= win_size + i * hop_size - 1:
            search_up_lim = search_up_lim + p0[i]
            local_m = np.append(local_m, local_m[-1] + p0[i])

        m = np.append(m, local_m)
        last_m = local_m[-1]

    m = np.sort(m)
    m = np.unique(m)
    m = m[1:]

    return m.astype(int)

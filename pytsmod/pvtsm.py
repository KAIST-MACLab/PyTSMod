import numpy as np
from scipy.interpolate import interp1d
from .utils import stft, istft, _validate_audio, _validate_scale_factor


def phase_vocoder(x, s, win_type='sin', win_size=2048, syn_hop_size=512,
                  zero_pad=0, restore_energy=False, fft_shift=False,
                  phase_lock=False):
    """Modify length of the audio sequence using Phase Vocoder algorithm.

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
                type of the window function for the STFT.
                hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    syn_hop_size : int > 0 [scalar]
                    hop size of the synthesis window.
                    Usually half of the window size.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    restore_energy : bool
                     tries to reserve potential energy loss.
    fft_shift : bool
                apply circular shift to STFT and ISTFT.
    phase_lock : bool
                 apply phase locking.

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

    sw_pos = np.arange(0, output_length + win_size // 2, syn_hop_size)
    ana_interpolated = interp1d(anc_points[1, :], anc_points[0, :],
                                fill_value='extrapolate')
    aw_pos = np.round(ana_interpolated(sw_pos)).astype(int)
    ana_hop = np.insert(aw_pos[1:] - aw_pos[0: -1], 0, 0)

    y = np.zeros((n_chan, output_length))

    for c, x_chan in enumerate(x):
        X = stft(x_chan, ana_hop=aw_pos, win_type=win_type,
                 win_size=win_size, zero_pad=zero_pad, fft_shift=fft_shift)

        Y = np.zeros(X.shape, dtype=np.complex)
        Y[:, 0] = X[:, 0]  # phase initialization

        N = win_size + zero_pad
        k = np.arange(N / 2 + 1)

        omega = 2 * np.pi * k / N

        for i in range(1, X.shape[1]):
            dphi = omega * ana_hop[i]

            ph_curr = np.angle(X[:, i])
            ph_last = np.angle(X[:, i - 1])

            hpi = (ph_curr - ph_last) - dphi
            hpi = hpi - 2 * np.pi * np.round(hpi / (2 * np.pi))

            ipa_sample = (omega + hpi / ana_hop[i])

            ipa_hop = ipa_sample * syn_hop_size

            ph_syn = np.angle(Y[:, i - 1])

            if phase_lock:
                p, ir = _find_peaks(X[:, i])

                theta = np.zeros(Y[:, i].shape)
                for n in range(len(p)):
                    theta[ir[0, n]: ir[1, n] + 1] = ph_syn[p[n]] + ipa_hop[p[n]] - ph_curr[p[n]]

                phasor = np.exp(1j * theta)
            else:
                theta = ph_syn + ipa_hop - ph_curr
                phasor = np.exp(1j * theta)

            Y[:, i] = phasor * X[:, i]

        y_chan = istft(Y, syn_hop=syn_hop_size, win_type=win_type,
                       win_size=win_size, zero_pad=zero_pad, num_iter=1,
                       original_length=output_length, fft_shift=fft_shift,
                       restore_energy=restore_energy)

        y[c, :] = y_chan

    return y.squeeze()


def phase_vocoder_int(x, s, win_type='hann', win_size=2048, syn_hop_size=512,
                      zero_pad=None, restore_energy=False, fft_shift=True):
    """Modify length of the audio sequence using Phase Vocoder algorithm.
    Works specially well for integer stretching.

    Parameters
    ----------
    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to modify.
    alpha : int > 0 [scalar]
        the time stretching factor.
        Only a integer value greater than 0 is allowed.
    win_type : str
               type of the window function for the STFT.
               hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    syn_hop_size : int > 0 [scalar]
                   hop size of the synthesis window.
                   Usually half of the window size.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    restore_energy : bool
                     tries to reserve potential energy loss.
    fft_shift : bool
                apply circular shift to STFT and ISTFT.

    Returns
    -------

    y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the modified output audio sequence.
    """
    # validate the input audio and scale factor.
    x = _validate_audio(x)
    if np.isscalar(s) and isinstance(s, int) and s >= 1:
        anchor_points = np.array([[0, np.shape(x)[1] - 1],
                                  [0, np.ceil(s * np.shape(x)[1]) - 1]])
    else:
        raise Exception("Please use the valid stretching rate. "
                        + "(integer stretching factors larger than 0)")

    if zero_pad is None:
        zero_pad = s * win_size // 2

    output_length = int(anchor_points[-1, -1]) + 1

    out_win_pos = np.arange(0, output_length + win_size // 2, syn_hop_size)
    in_win_pos = ((out_win_pos - 1) / s + 1).astype(int)

    n_channels = x.shape[0]
    y = np.zeros((n_channels, output_length))

    for c, x_chan in enumerate(x):
        X = stft(x_chan, ana_hop=in_win_pos, win_type=win_type,
                 win_size=win_size, zero_pad=zero_pad, fft_shift=fft_shift)
        Y = abs(X) * np.exp(1j * s * np.angle(X))

        y_chan = istft(Y, syn_hop=syn_hop_size, win_type=win_type,
                       win_size=win_size, zero_pad=zero_pad, num_iter=1,
                       original_length=output_length,
                       restore_energy=restore_energy, fft_shift=fft_shift)

        y[c, :] = y_chan

    return y.squeeze()


def _find_peaks(spec):
    """ Find indices of peaks in spectrogram.
    A value which it the largest value among its four nearest neighbors
    is treated as a peak.

    Parameters
    ----------
    spec : numpy.ndarray [shape=(num_bins)]
           A single frame from the STFT.

    Returns
    -------

    peaks : numpy.ndarray [shape=(num_peaks)]
            an array with peaks in the STFT frame.
    infl_region: numpy.ndarray [shape=(2, num_peaks)]
            Region of influence for each peak.
    """

    mag_spec = np.abs(spec)
    mag_spec_padded = np.pad(mag_spec, 2, 'constant')

    peaks = ((mag_spec_padded[4:] < mag_spec)
             * (mag_spec_padded[3: -1] < mag_spec)
             * (mag_spec_padded[1: -3] < mag_spec)
             * (mag_spec_padded[: -4] < mag_spec))
    peaks = np.where(peaks)[0]

    if peaks.size == 0:
        return peaks, np.empty(0)

    # Find region of influence. Axis 0 represents start and end each.
    infl_region = np.zeros((2, peaks.size))
    infl_region[0, 0] = 0
    infl_region[0, 1:] = np.ceil((peaks[1:] + peaks[: -1]) / 2)
    infl_region[1, : -1] = infl_region[0, 1:] - 1
    infl_region[1, -1] = spec.size - 1

    return peaks, infl_region.astype(int)

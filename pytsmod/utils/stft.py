import numpy as np
from .win import win as win_func


def stft(x, ana_hop=2048, win_type='hann', win_size=4096, zero_pad=0, sr=44100,
         fft_shift=0, time_frequency_out=False):
    """Short-Time Fourier Transform (STFT) for the audio signal.
    This function is used for phase vocoder.

    Parameters
    ----------
    x : numpy.ndarray [shape=(num_samples)]
        the input audio sequence. Should be a single channel.
    ana_hop : int > 0 [scalar] or numpy.ndarray [shape=(num_frames)]
              either a analysis hop size (scalar)
              or analyze window positions (array).
    win_type : str
               type of the window function for the STFT.
               hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    sr : int > 0 [scalar]
         the sample rate of the audio sequence. Only used for time_frequency_out.
    fft_shift : bool
                apply circular shift to STFT.
    time_frequency_out : bool
                         returns time and frequency axis indices
                         in (spec, t, f).

    Returns
    -------

    spec : numpy.ndarray [shape=(win_size // 2 + 1, num_frames)]
           the STFT result of the input audio sequence.
    t : numpy.ndarray [shape=num_frames]
        timestamp of the output result.
    f : numpy.ndarray [shape=win_size // 2 + 1]
        frequency value for each frequency bin of the output result.
    """

    win = win_func(win_type=win_type, win_size=win_size, zero_pad=zero_pad)
    win_size = win.size

    max_ana_hop = np.max(ana_hop)
    x_padded = np.pad(x, (win_size // 2, win_size + max_ana_hop), 'constant')

    if np.isscalar(ana_hop):
        num_frames = int((len(x_padded) - win_size) / ana_hop + 1)
        win_pos = np.arange(num_frames) * ana_hop
    else:
        num_frames = ana_hop.size
        win_pos = ana_hop[0:num_frames]

    spec = np.zeros((win_size // 2 + 1, num_frames), dtype=np.complex)
    for i in range(num_frames):
        xi = x_padded[win_pos[i]: win_pos[i] + win_size] * win

        if fft_shift:
            xi = np.append(xi[len(xi) // 2:], xi[0: len(xi) // 2])
        Xi = np.fft.fft(xi)
        spec[:, i] = Xi[0: win_size // 2 + 1]

    if time_frequency_out:
        t = (win_pos - 1) / sr
        f = np.arange(0, win_size / 2) * sr / win_size
        return spec, t, f
    else:
        return spec


def istft(spec, syn_hop=2048, win_type='hann', win_size=4096, zero_pad=0,
          num_iter=1, original_length=-1, fft_shift=False,
          restore_energy=False):
    """Inverse Short-Time Fourier Transform to recover the audio signal
    from the spectrogram. This function is used for phase vocoder.

    Parameters
    ----------

    X : numpy.ndarray [shape=(num_bins, num_frames)]
        the input audio complex spectrogram.
    syn_hop : int > 0 [scalar]
              the hop size of the synthesis window.
    win_type : str
               type of the window function for the ISTFT.
               hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    num_iter : int > 0 [scalar]
               the number of iterations the algorihm should perform
               to adapt the phase.
    original_length : int > 0 [scalar]
                      original length of the audio signal.
    fft_shift : bool
                apply circular shift to ISTFT.
    restore_energy : bool
                     tries to reserve potential energy loss.

    Returns
    -------

    y : numpy.ndarray [shape=(original_length)]
        the output audio sequence.
    """

    Yi = spec
    yi = lsee_mstft(Yi, syn_hop, win_type, win_size,
                    zero_pad, fft_shift, restore_energy)

    for _ in range(1, num_iter):
        Yi = np.abs(spec) * np.exp(1j*np.angle(stft(yi, ana_hop=syn_hop,
                                                    win_type=win_type,
                                                    win_size=win_size,
                                                    zero_pad=zero_pad)))
        yi = lsee_mstft(Yi, syn_hop, win_type, win_size,
                        zero_pad, fft_shift, restore_energy)

    y = yi

    if original_length > 0:
        y = y[: original_length]

    return y


def lsee_mstft(X, syn_hop, win_type, win_size, zero_pad, fft_shift,
               restore_energy):
    """Least Squares Error Estimation from the MSTFT (Modified STFT).
    Griffin-Lim procedure to estimate the audio signal from the modified STFT.

    Parameters
    ----------

    X : numpy.ndarray [shape=(num_bins, num_frames)]
        the input audio complex spectrogram.
    syn_hop : int > 0 [scalar]
              the hop size of the synthesis window.
    win_type : str
               type of the window function for the ISTFT.
               hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    fft_shift : bool
                apply circular shift to ISTFT.
    restore_energy : bool
                     tries to reserve potential energy loss.

    Returns
    -------

    x : numpy.ndarray [shape=num_samples]
        the output audio sequence through LSEE_MSTFT
    """

    w = win_func(win_type, win_size, zero_pad)

    win_len = len(w)
    n_frames = X.shape[1]
    win_pos = np.arange(n_frames) * syn_hop
    signal_length = win_pos[-1] + win_len

    x = np.zeros(signal_length)
    ow = np.zeros(signal_length)
    for i in range(n_frames):
        curr_spec = X[:, i]

        Xi = np.append(curr_spec, np.flip(np.conj(curr_spec[1:-1])))
        xi = np.real(np.fft.ifft(Xi))
        if fft_shift:
            xi = np.fft.fftshift(xi)

        xiw = xi * w

        if restore_energy:
            xi_energy = np.sum(abs(xi))
            xiw_energy = np.sum(abs(xiw))
            xiw = xiw * (xi_energy / (xiw_energy + np.finfo(np.float).eps))

        x[win_pos[i]: win_pos[i] + win_len] += xiw

        ow[win_pos[i]: win_pos[i] + win_len] += np.power(w, 2)

    ow[ow < 1e-3] = 1
    x = x / ow

    x = x[win_len // 2: - win_len // 2]

    return x

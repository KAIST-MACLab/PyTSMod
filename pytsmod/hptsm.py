from scipy.ndimage import median_filter
import numpy as np
from .pvtsm import phase_vocoder
from .olatsm import ola
from .utils import _validate_audio, stft, istft


def hptsm(x, s, hp_len_harm=10, hp_len_perc=10, hp_mask_mode='binary', hp_win_type='hann',
          hp_win_size=1024, hp_hop_size=256, hp_zero_pad=0, hp_fft_shift=False,
          pv_win_type='hann', pv_win_size=2048, pv_syn_hop_size=512,
          pv_zero_pad=0, pv_restore_energy=False, pv_fft_shift=False,
          pv_phase_lock=True, ola_win_type='hann',
          ola_win_size=256, ola_syn_hop_size=128):
    """Modify length of the audio sequence using both Phase Vocoder and OLA.
    Apply Phase Vocoder to harmonic signal, and apply OLA to percussive signal.
    For HPSS, median filter based algorithm is used.

    Parameters
    ----------

    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to modify.
    s : number > 0 [scalar] or numpy.ndarray [shape=(2, num_points)]
        the time stretching factor. Either a constant value (alpha)
        or an 2 x n array of anchor points which contains the sample points
        of the input signal in the first row
        and the sample points of the output signal in the second row.
    hp_ : parameters for HPSS.
    pv_ : parameters for phase vocoder.
    ola_ : parameters for OLA.

    Returns
    -------

    y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the modified output audio sequence.
    """
    x = _validate_audio(x)

    x_harm, x_perc = _hpss(x, len_harm=hp_len_harm, len_perc=hp_len_perc, mask_mode=hp_mask_mode,
                           win_type=hp_win_type, win_size=hp_win_size, hop_size=hp_hop_size,
                           zero_pad=hp_zero_pad, fft_shift=hp_fft_shift)

    y_harm = phase_vocoder(x_harm, s, win_type=pv_win_type,
                           win_size=pv_win_size, syn_hop_size=pv_syn_hop_size,
                           zero_pad=pv_zero_pad,
                           restore_energy=pv_restore_energy,
                           fft_shift=pv_fft_shift,
                           phase_lock=pv_phase_lock)
    y_perc = ola(x_perc, s, win_type=ola_win_type, win_size=ola_win_size,
                 syn_hop_size=ola_syn_hop_size)

    return y_harm + y_perc


def _hpss(x, len_harm=10, len_perc=10, mask_mode='binary', win_type='hann',
          win_size=1024, hop_size=256, zero_pad=0, fft_shift=False):
    """Separate the input audio sequence to a harmonic and a percussive source.
    The algorithm is from the following paper.

    Derry Fitzgerald, "Harmonic/percussive separation using median filtering." Proc. of the Int. Conf. on Digital Audio Effects (DAFx). Vol. 13. 2010.

    Parameters
    ----------

    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to separate.
    len_harm : int
               length of the median filter kernel size for the harmonic source.
    len_perc : int
               length of the median filter kernel size for the percussive source.
    mask_mode : str
                mask mode for the separation. binary and relative are available.
    win_type : str
               type of the window function for the STFT. hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function for the STFT and the ISTFT.
    hop_size : int > 0 [scalar]
               hop size of the analysis/synthesis window for the STFT and the ISTFT.
    zero_pad : int > 0 [scalar]
               the size of the zero pad in the window function.
    fft_shift : bool
                apply circular shift to STFT and ISTFT.

    Returns
    -------

    x_harm : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
             the separated harmonic audio sequence.
    x_perc : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
             the separated percussive audio sequence.
    """
    x_harm = np.zeros(x.shape)
    x_perc = np.zeros(x.shape)

    for c, x_chan in enumerate(x):
        spec = stft(x_chan, ana_hop=hop_size, win_type=win_type, win_size=win_size,
                    zero_pad=zero_pad, fft_shift=fft_shift)
        mag_spec = np.abs(spec)

        mag_spec_harm = median_filter(mag_spec, size=[1, len_harm], mode='reflect')
        mag_spec_perc = median_filter(mag_spec, size=[len_perc, 1], mode='reflect')

        if mask_mode == 'binary':
            mask_harm = mag_spec_harm > mag_spec_perc
            mask_perc = mag_spec_harm <= mag_spec_perc
        elif mask_mode == 'relative':
            mask_harm = mag_spec_harm / (mag_spec_harm + mag_spec_perc + np.finfo(float).eps)
            mask_perc = mag_spec_perc / (mag_spec_harm + mag_spec_perc + np.finfo(float).eps)
        else:
            raise Exception("Please use the valid mask mode. (binary, relative)")

        spec_harm = mask_harm * spec
        spec_perc = mask_perc * spec

        x_harm[c, :] = istft(spec_harm, syn_hop=hop_size, win_type=win_type, win_size=win_size,
                             zero_pad=zero_pad, original_length=x.shape[1], fft_shift=fft_shift)
        x_perc[c, :] = istft(spec_perc, syn_hop=hop_size, win_type=win_type, win_size=win_size,
                             zero_pad=zero_pad, original_length=x.shape[1], fft_shift=fft_shift)

    return x_harm.squeeze(), x_perc.squeeze()

from librosa.effects import hpss
import numpy as np
from .pvtsm import phase_vocoder
from .olatsm import ola
from .utils import _validate_audio


def hptsm(x, s, hp_kernel_size=31, hp_power=2.0, hp_mask=False, hp_margin=1.0,
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
    x_harm = np.zeros(x.shape)
    x_perc = np.zeros(x.shape)

    for c, x_chan in enumerate(x):
        x_harm_chan, x_perc_chan = hpss(x_chan, kernel_size=hp_kernel_size,
                                        power=hp_power, mask=hp_mask,
                                        margin=hp_margin)
        x_harm[c, :] = x_harm_chan
        x_perc[c, :] = x_perc_chan

    y_harm = phase_vocoder(x_harm, s, win_type=pv_win_type,
                           win_size=pv_win_size, syn_hop_size=pv_syn_hop_size,
                           zero_pad=pv_zero_pad,
                           restore_energy=pv_restore_energy,
                           fft_shift=pv_fft_shift,
                           phase_lock=pv_phase_lock)
    y_perc = ola(x_perc, s, win_type=ola_win_type, win_size=ola_win_size,
                 syn_hop_size=ola_syn_hop_size)

    return y_harm + y_perc

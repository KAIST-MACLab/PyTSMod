import numpy as np
from warnings import warn


def _validate_audio(audio):
    """validate the input audio and modify the order of channels.

    Parameters
    ----------

    audio : numpy.ndarray [shape=(channel, num_samples) or (num_samples)
                           or (num_samples, channel)]
            the input audio sequence to validate.

    Returns
    -------

    audio : numpy.ndarray [shape=(channel, num_samples)]
            the validataed output audio sequence.
    """
    if audio.ndim == 1:
        audio = np.expand_dims(audio, 0)
    elif audio.ndim > 2:
        raise Exception("Please use the valid audio source. "
                        + "Number of dimension of input should be less than 3.")
    elif audio.shape[0] > audio.shape[1]:
        warn('it seems that the 2nd axis of the input audio source '
             + 'is a channel. it is recommended that fix channel '
             + 'to the 1st axis.', stacklevel=3)
        audio = audio.T

    return audio


def _validate_scale_factor(audio, s):
    """Validate the scale factor s and
    convert the fixed scale factor to anchor points.

    Parameters
    ----------

    audio : numpy.ndarray [shape=(num_channels, num_samples)]
            the input audio sequence.
    s : number > 0 [scalar]
        or numpy.ndarray [shape=(2, num_points) or (num_points, 2)]
        the time stretching factor. Either a constant value (alpha)
        or an (2 x n) (or (n x 2)) array of anchor points
        which contains the sample points of the input signal in the first row
        and the sample points of the output signal in the second row.

    Returns
    -------

    anc_points : numpy.ndarray [shape=(2, num_points)]
                 anchor points which contains the sample points
                 of the input signal in the first row
                 and the sample points of the output signal in the second row.
    """
    if np.isscalar(s):
        anc_points = np.array([[0, np.shape(audio)[1] - 1],
                               [0, np.ceil(s * np.shape(audio)[1]) - 1]])
    elif s.ndim == 2:
        if s.shape[0] == 2:
            anc_points = s
        elif s.shape[1] == 2:
            warn('it seems that the anchor points '
                 + 'has shape (num_points, 2). '
                 + 'it is recommended to '
                 + 'have shape (2, num_points).', stacklevel=3)
            anc_points = s.T
    else:
        raise Exception('Please use the valid anchor points. '
                        + '(scalar or pair of input/output sample points)')

    return anc_points


if __name__ == '__main__':
    x = np.array([[1,2,3,4,5], [6,7,8,9,0]])
    _validate_audio(x.T)

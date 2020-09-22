from .wsolatsm import wsola


def ola(x, s, win_type='hann', win_size=1024, syn_hop_size=512):
    """Modify length of the audio sequence using OLA algorithm.
    WSOLA with zero tolerance is working same as OLA.

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

     Returns
     -------

     y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
         the modified output audio sequence.
    """
    return wsola(x, s, win_type=win_type, win_size=win_size,
                 syn_hop_size=syn_hop_size, tolerance=0)

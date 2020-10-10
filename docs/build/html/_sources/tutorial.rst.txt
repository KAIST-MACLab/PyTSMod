Tutorial
********

Using OLA and WSOLA, and PV-TSM
===============================
OLA, WSOLA, and PV-TSM can be imported as module to be used directly in Python. To get the result easily, all you need is just two parameters, the input audio sequence x and the time stretching factor s. Here's a minimal example:

.. code-block:: python
    :linenos:

    import numpy as np
    import pytsmod as tsm
    import soundfile as sf  # you can use other audio load packages.

    x, sr = sf.read('/FILEPATH/AUDIOFILE.wav')
    x = x.T  # if the input is multichannel audio, it is recommended to use the shape (num_channels, audio_len)
    x_length = x.shape[-1]

    s_fixed = 1.3  # stretch the audio signal 1.3x times.
    s_ap = np.array([[0, x_length / 2, x_length], [0, x_length, x_length * 1.5]])  # double the first half of the audio only and preserve the other half.

    x_s_fixed = tsm.wsola(x, s_fixed)
    x_s_ap = tsm.wsola(x, s_ap)

Time stretching factor s
----------------------------
Time stretching factor s can either be a constant value (alpha) or an 2 x n array of anchor points which contains the sample points of the input signal in the first row and the sample points of the output signal in the second row.

Using TD-PSOLA
==============
When using TD-PSOLA, the estimated pitch information of the source you want to modify is needed. Also, you should know the hop size and frame length of the pitch tracking algorithm you used. Here's a minimal example:

.. code-block:: python
    :linenos:

    import numpy as np
    import pytsmod as tsm
    import crepe  # you can use other pitch tracking algorithms.
    import soundfile as sf  # you can use other audio load packages.

    x, sr = sf.read('/FILEPATH/AUDIOFILE.wav')

    _, f0_crepe, _, _ = crepe.predict(x, sr, viterbi=True, step_size=10)

    x_double_stretched = tsm.tdpsola(x, sr, f0_crepe, alpha=2, p_hop_size=441, p_win_size=1470)  # hop_size and frame_length for CREPE step_size=10 with sr=44100
    x_3keyup = tsm.tdpsola(x, sr, f0_crepe, beta=pow(2, 3/12), p_hop_size=441, p_win_size=1470)
    x_3keydown = tsm.tdpsola(x, sr, f0_crepe, target_f0=f0_crepe * pow(2, -3/12), p_hop_size=441, p_win_size=1470)

Time stretching factor alpha
----------------------------
In this version, TD-PSOLA only supports the fixed time stretching factor alpha.

Pitch shifting factor beta and target_f0
----------------------------------------
You can modify pitch of the audio sequence in two ways. The first one is beta, which is the fixed pitch shifting factor. The other one is target_f0, which supports target pitch sequence you want to convert. You cannot use both of the parameters.

Command-Line Interface
======================
From version 0.3.0, this package includes a command-line tool named ``tsmod``, which can create the result file easily from a shell. To generate the WSOLA result of ``input.wav`` with stretching factor 1.3 and save to ``output.wav``, please run::

$ tsmod wsola input.wav output.wav 1.3  # ola, wsola, pv, pv_int are available.

Currently, OLA, WSOLA, and Phase Vocoder(PV) are supported. TD-PSOLA is excluded due to the difficulty of sending extracted pitch data to TD-PSOLA. Also, non-linear TSM is not supported in command-line.

For more information, use ``-h`` or ``--help`` command to see the detailed usage of ``tsmod``.
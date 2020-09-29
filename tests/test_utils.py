import pytest
import pytsmod as tsm
from scipy.io import loadmat
import soundfile as sf
import numpy as np


@pytest.mark.parametrize('ana_hop', [1024, 2048])
@pytest.mark.parametrize('win_type', ['hann', 'sin'])
@pytest.mark.parametrize('win_size', [2048, 4096])
@pytest.mark.parametrize('zero_pad', [0, 512])
@pytest.mark.parametrize('fft_shift', [0, 1])
def test_stft(ana_hop, win_type, win_size, zero_pad, fft_shift):
    x, _ = sf.read('tests/data/castanetsviolin.wav')
    matlab_results = loadmat('tests/data/stft.mat')['result']

    X = tsm.utils.stft(x, ana_hop, win_type, win_size, zero_pad,
                       fft_shift=fft_shift)

    _, w = np.where(matlab_results[0, :] == np.array([[ana_hop]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[1, :] == np.array([[2 if win_type == 'hann' else 1]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[2, :] == np.array([[win_size]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[3, :] == np.array([[zero_pad]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[4, :] == np.array([[fft_shift]]))
    matlab_results = matlab_results[:, w]

    X_matlab = matlab_results[5, :][0]
    assert np.allclose(X, X_matlab)

    matlab_results = loadmat('tests/data/istft.mat')['result']

    x = tsm.utils.istft(X, ana_hop, win_type, win_size, zero_pad,
                        fft_shift=fft_shift)

    _, w = np.where(matlab_results[0, :] == np.array([[ana_hop]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[1, :] == np.array([[2 if win_type == 'hann' else 1]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[2, :] == np.array([[win_size]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[3, :] == np.array([[zero_pad]]))
    matlab_results = matlab_results[:, w]
    _, w = np.where(matlab_results[4, :] == np.array([[fft_shift]]))
    matlab_results = matlab_results[:, w]

    x_matlab = matlab_results[5, :][0].squeeze()
    assert np.allclose(x, x_matlab)

import pytest
import pytsmod as tsm
import numpy as np
from scipy.io import loadmat
import soundfile as sf


@pytest.mark.parametrize('alpha', [0.75, 1, 1.25])
@pytest.mark.parametrize('win_type', ['hann', 'sin'])
@pytest.mark.parametrize('win_size', [1024, 2048])
@pytest.mark.parametrize('syn_hop_size', [512, 1024])
@pytest.mark.parametrize('tolerance', [512, 1024])
def test_wsola_fixed(alpha, win_type, win_size, syn_hop_size, tolerance):
    x, _ = sf.read('tests/data/castanetsviolin.wav')
    wsola_fixed_rate = loadmat('tests/data/wsola_fixed_rate.mat')

    y = tsm.wsola(x, alpha, win_type, win_size, syn_hop_size, tolerance)

    sample_name = (f'cas_{str(int(alpha * 100)).zfill(3)}_'
                   + f'{win_type}_{win_size}_{syn_hop_size}_{tolerance}')
    y_matlab = wsola_fixed_rate[sample_name].squeeze()
    assert np.allclose(y, y_matlab)


@pytest.mark.parametrize('win_type', ['hann', 'sin'])
@pytest.mark.parametrize('win_size', [1024, 2048])
@pytest.mark.parametrize('syn_hop_size', [512, 1024])
@pytest.mark.parametrize('tolerance', [512, 1024])
def test_wsola_nonlinear(win_type, win_size, syn_hop_size, tolerance):
    x, _ = sf.read('tests/data/beethovenorchestra.wav')
    ap = loadmat('tests/data/anchorpoints.mat')['anchorpoints'].T - 1
    wsola_nonlinear = loadmat('tests/data/wsola_nonlinear.mat')

    y = tsm.wsola(x, ap, win_type, win_size, syn_hop_size, tolerance)

    sample_name = f'orc_{win_type}_{win_size}_{syn_hop_size}_{tolerance}'
    y_matlab = wsola_nonlinear[sample_name].squeeze()
    assert np.allclose(y, y_matlab)


@pytest.mark.parametrize('n_chan', range(2, 9))
@pytest.mark.parametrize('transpose', [True, False])
def test_wsola_multichannel(n_chan, transpose):
    x, _ = sf.read('tests/data/dogbeetle.wav')
    x_wsola = tsm.wsola(x, 1.3)

    x_multi = np.tile(x, (n_chan, 1))

    if transpose:
        x_multi = x_multi.T

    x_multi_wsola = tsm.wsola(x_multi, 1.3)

    for i in range(x_multi_wsola.shape[0]):
        assert np.allclose(x_wsola, x_multi_wsola[i, :])

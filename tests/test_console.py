import pytest
from pytsmod import ola, wsola
from pytsmod import phase_vocoder as pv
from pytsmod import phase_vocoder_int as pv_int
import soundfile as sf
import numpy as np
import os
from subprocess import call


@pytest.mark.parametrize('algorithm', ['ola', 'wsola', 'pv', 'pv_int'])
def test_console_default_params(algorithm):
    test_file = 'tests/data/castanetsviolin.wav'
    alpha = 2
    x, sr = sf.read(test_file)
    y = globals()[algorithm](x, alpha)

    cmd = ['python', 'pytsmod/console/console.py', algorithm,
           test_file, 'temp_cli.wav', str(alpha)]
    if algorithm == 'pv_int':
        cmd.append('-fs')
    call(cmd)

    sf.write('temp.wav', y, sr)
    y_, _ = sf.read('temp.wav')

    y_cli, _ = sf.read('temp_cli.wav')

    os.remove('temp.wav')
    os.remove('temp_cli.wav')

    assert np.allclose(y_, y_cli)


@pytest.mark.parametrize('alpha', [1.25])
@pytest.mark.parametrize('win_type', ['sin'])
@pytest.mark.parametrize('win_size', [512])
@pytest.mark.parametrize('syn_hop_size', [256])
def test_console_ola(alpha, win_type, win_size, syn_hop_size):
    test_file = 'tests/data/castanetsviolin.wav'
    x, sr = sf.read(test_file)
    y = ola(x, alpha, win_type=win_type, win_size=win_size,
            syn_hop_size=syn_hop_size)

    cmd = ['python', 'pytsmod/console/console.py', 'ola',
           test_file, 'temp_cli.wav', str(alpha),
           '-wt', win_type, '-ws', str(win_size),
           '-sh', str(syn_hop_size)]
    call(cmd)

    sf.write('temp.wav', y, sr)
    y_, _ = sf.read('temp.wav')

    y_cli, _ = sf.read('temp_cli.wav')

    os.remove('temp.wav')
    os.remove('temp_cli.wav')

    assert np.allclose(y_, y_cli)


@pytest.mark.parametrize('alpha', [1.25])
@pytest.mark.parametrize('win_type', ['sin'])
@pytest.mark.parametrize('win_size', [512])
@pytest.mark.parametrize('syn_hop_size', [256])
@pytest.mark.parametrize('tolerance', [256])
def test_console_wsola(alpha, win_type, win_size, syn_hop_size, tolerance):
    test_file = 'tests/data/castanetsviolin.wav'
    x, sr = sf.read(test_file)
    y = wsola(x, alpha, win_type=win_type, win_size=win_size,
              syn_hop_size=syn_hop_size, tolerance=tolerance)

    cmd = ['python', 'pytsmod/console/console.py', 'wsola',
           test_file, 'temp_cli.wav', str(alpha),
           '-wt', win_type, '-ws', str(win_size),
           '-sh', str(syn_hop_size), '-t', str(tolerance)]
    call(cmd)

    sf.write('temp.wav', y, sr)
    y_, _ = sf.read('temp.wav')

    y_cli, _ = sf.read('temp_cli.wav')

    os.remove('temp.wav')
    os.remove('temp_cli.wav')

    assert np.allclose(y_, y_cli)


@pytest.mark.parametrize('alpha', [1.25])
@pytest.mark.parametrize('win_type', ['hann'])
@pytest.mark.parametrize('win_size', [1024])
@pytest.mark.parametrize('syn_hop_size', [256])
@pytest.mark.parametrize('zero_pad', [256])
@pytest.mark.parametrize('restore_energy', [True])
@pytest.mark.parametrize('fft_shift', [True])
@pytest.mark.parametrize('phase_lock', [True])
def test_console_pv(alpha, win_type, win_size, syn_hop_size, zero_pad,
                    restore_energy, fft_shift, phase_lock):
    test_file = 'tests/data/castanetsviolin.wav'
    x, sr = sf.read(test_file)
    y = pv(x, alpha, win_type=win_type, win_size=win_size,
           syn_hop_size=syn_hop_size, zero_pad=zero_pad,
           restore_energy=restore_energy, fft_shift=fft_shift,
           phase_lock=phase_lock)

    cmd = ['python', 'pytsmod/console/console.py', 'pv',
           test_file, 'temp_cli.wav', str(alpha),
           '-wt', win_type, '-ws', str(win_size),
           '-sh', str(syn_hop_size), '-z', str(zero_pad),
           '-e', '-fs', '-pl']
    call(cmd)

    sf.write('temp.wav', y, sr)
    y_, _ = sf.read('temp.wav')

    y_cli, _ = sf.read('temp_cli.wav')

    os.remove('temp.wav')
    os.remove('temp_cli.wav')

    assert np.allclose(y_, y_cli)


@pytest.mark.parametrize('alpha', [2])
@pytest.mark.parametrize('win_type', ['sin'])
@pytest.mark.parametrize('win_size', [1024])
@pytest.mark.parametrize('syn_hop_size', [256])
@pytest.mark.parametrize('zero_pad', [256])
@pytest.mark.parametrize('restore_energy', [True])
@pytest.mark.parametrize('fft_shift', [False])
def test_console_pv_int(alpha, win_type, win_size, syn_hop_size, zero_pad,
                        restore_energy, fft_shift):
    test_file = 'tests/data/castanetsviolin.wav'
    x, sr = sf.read(test_file)
    y = pv(x, alpha, win_type=win_type, win_size=win_size,
           syn_hop_size=syn_hop_size, zero_pad=zero_pad,
           restore_energy=restore_energy, fft_shift=fft_shift)

    cmd = ['python', 'pytsmod/console/console.py', 'pv',
           test_file, 'temp_cli.wav', str(alpha),
           '-wt', win_type, '-ws', str(win_size),
           '-sh', str(syn_hop_size), '-z', str(zero_pad),
           '-e']
    call(cmd)

    sf.write('temp.wav', y, sr)
    y_, _ = sf.read('temp.wav')

    y_cli, _ = sf.read('temp_cli.wav')

    os.remove('temp.wav')
    os.remove('temp_cli.wav')

    assert np.allclose(y_, y_cli)

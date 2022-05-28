# PyTSMod

[![PyPI](https://img.shields.io/pypi/v/pytsmod.svg)](https://pypi.python.org/pypi/pytsmod)
[![Build Status](https://img.shields.io/github/workflow/status/KAIST-MACLab/PyTSMod/Python%20package)](https://github.com/KAIST-MACLab/PyTSMod/actions/workflows/python-package.yml)
![Python](https://img.shields.io/pypi/pyversions/pytsmod.svg)
![license](https://img.shields.io/github/license/KAIST-MACLab/PyTSMod.svg)
![downloads](https://img.shields.io/pypi/dm/pytsmod.svg)

PyTSMod is a open-source library for Time-Scale Modification algorithms in Python 3. PyTSMod contains basic TSM algorithms such as Overlap-Add (OLA), Waveform-Similarity Overlap-Add (WSOLA), Time-Domain Pitch-Synchronous Overlap-Add (TD-PSOLA), and Phase Vocoder (PV-TSM). We are also planning to add more TSM algorithms and pitch shifting algorithms.

Full documentation is available on <https://pytsmod.readthedocs.io>

![open-issues](https://img.shields.io/github/issues/KAIST-MACLab/pytsmod.svg)
![closed-issues](https://img.shields.io/github/issues-closed/KAIST-MACLab/pytsmod.svg)
![open-prs](https://img.shields.io/github/issues-pr/KAIST-MACLab/pytsmod.svg)
![closed-prs](https://img.shields.io/github/issues-pr-closed/KAIST-MACLab/pytsmod.svg)

The implementation of the algorithms are based on those papers and libraries:

> [TSM Toolbox: MATLAB Implementations of Time-Scale Modification Algorithms.](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/2014_DriedgerMueller_TSM-Toolbox_DAFX.pdf)<br>
> Jonathan Driedger, Meinard Müller.<br>
> Proceedings of the 17th International Conference on Digital Audio Effects (DAFx-14), 2014.

> [A review of time-scale modification of music signals.](https://www.mdpi.com/2076-3417/6/2/57htm)<br>
> Jonathan Driedger, Meinard Müller.<br>
> Applied Sciences, 6(2), 57, 2016.

> [DAFX: digital audio effects](https://books.google.co.kr/books?hl=ko&lr=&id=DX-mRhkJL74C&oi=fnd&pg=PT7&dq=Dafx+book&ots=EMFASHiHrs&sig=Mtft4q1dJgFXjOsDnLyMN9eKMRQ#v=onepage&q=Dafx%20book&f=false)<br>
> Udo Zölzer.<br>
> John Wiley & Sons, 2011.


## Installing PyTSMod

PyTSMod is hosted on PyPI. To install, run the following command in your Python environment:

```bash
$ pip install pytsmod
```

Or if you use [poetry](https://python-poetry.org), you can clone the repository and build the package through the following command:

```bash
$ poetry build
```

### Requirements

To use the latest version of PyTSMod, Python with version >= 3.8 and following packages are required.

- NumPy (>=1.20.0)
- SciPy (>=1.8.0)
- soundfile (>=0.10.0)

## Using PyTSMod

### Using OLA, WSOLA, and PV-TSM

OLA, WSOLA, and PV-TSM can be imported as module to be used directly in Python. To get the result easily, all you need is just two parameters, the input audio sequence x and the time stretching factor s. Here's a minimal example:

```python
import numpy as np
import pytsmod as tsm
import soundfile as sf  # you can use other audio load packages.

x, sr = sf.read('/FILEPATH/AUDIOFILE.wav')
x = x.T
x_length = x.shape[-1]  # length of the audio sequence x.

s_fixed = 1.3  # stretch the audio signal 1.3x times.
s_ap = np.array([[0, x_length / 2, x_length], [0, x_length, x_length * 1.5]])  # double the first half of the audio only and preserve the other half.

x_s_fixed = tsm.wsola(x, s_fixed)
x_s_ap = tsm.wsola(x, s_ap)
```

#### Time stretching factor s

Time stretching factor s can either be a constant value (alpha) or an 2 x n array of anchor points which contains the sample points of the input signal in the first row and the sample points of the output signal in the second row.


### Using TD-PSOLA

When using TD-PSOLA, the estimated pitch information of the source you want to modify is needed. Also, you should know the hop size and frame length of the pitch tracking algorithm you used. Here's a minimal example:

```python
import numpy as np
import pytsmod as tsm
import crepe  # you can use other pitch tracking algorithms.
import soundfile as sf  # you can use other audio load packages.

x, sr = sf.read('/FILEPATH/AUDIOFILE.wav')

_, f0_crepe, _, _ = crepe.predict(x, sr, viterbi=True, step_size=10)

x_double_stretched = tsm.tdpsola(x, sr, f0_crepe, alpha=2, p_hop_size=441, p_win_size=1470)  # hop_size and frame_length for CREPE step_size=10 with sr=44100
x_3keyup = tsm.tdpsola(x, sr, f0_crepe, beta=pow(2, 3/12), p_hop_size=441, p_win_size=1470)
x_3keydown = tsm.tdpsola(x, sr, f0_crepe, target_f0=f0_crepe * pow(2, -3/12), p_hop_size=441, p_win_size=1470)
```

#### Time stretching factor alpha

In this version, TD-PSOLA only supports the fixed time stretching factor alpha.

#### Pitch shifting factor beta and target_f0

You can modify pitch of the audio sequence in two ways. The first one is beta, which is the fixed pitch shifting factor. The other one is target_f0, which supports target pitch sequence you want to convert. You cannot use both of the parameters.

### Using PyTSMod from the command line

From version 0.3.0, this package includes a command-line tool named `tsmod`, which can create the result file easily from a shell. To generate the WSOLA result of `input.wav` with stretching factor 1.3 and save to `output.wav`, please run:

```shell
$ tsmod wsola input.wav output.wav 1.3  # ola, wsola, pv, pv_int are available.
```

Currently, OLA, WSOLA, and Phase Vocoder(PV) are supported. TD-PSOLA is excluded due to the difficulty of sending extracted pitch data to TD-PSOLA. Also, non-linear TSM is not supported in command-line.

For more information, use `-h` or `--help` command to see the detailed usage of `tsmod`.

## Audio examples

The original audio is from TSM toolbox.

### Stretching factor α=0.5

| Name | Method | Original | OLA | WSOLA | Phase Vocoder | Phase Vocoder (phase locking) | TSM based on HPSS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| CastanetsViolin | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_0.50_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_0.50_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_0.50_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_0.50_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_0.50_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/12W-koxh8OkyrzEHibVifoYtWmuKCIbxy/view?usp=sharing) | [wav](https://drive.google.com/file/d/1juWR2-jx5rlPLv2JxhIiJZa83T7kgp3C/view?usp=sharing) | [wav](https://drive.google.com/file/d/1KdiTUkpdm1qMmMkdqkrMJhoRW_asUoqJ/view?usp=sharing) | [wav](https://drive.google.com/file/d/1dTSeSxkUGAEW75fpgFQXE9VoRuu3cgUR/view?usp=sharing) | [wav](https://drive.google.com/file/d/1W7saDSQCYEOc2ahqi7D4fAPZc2bCryrm/view?usp=sharing) |
| DrumSolo | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_0.50_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_0.50_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_0.50_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_0.50_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_0.50_HP.wav)
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1RD-rK0yInskaWuDhuKGPxMc1zzIMZFSv/view?usp=sharing) | [wav](https://drive.google.com/file/d/1PCxQTpzHbub-tpnqFYpbR-SEOpjq5L1m/view?usp=sharing) | [wav](https://drive.google.com/file/d/1QXbRdHN3UVBmnXax_FpNDPf3dAyKIlhi/view?usp=sharing) | [wav](https://drive.google.com/file/d/1vRPXSfgyvnTPVgSTGeryBtReYqFC1GC8/view?usp=sharing) | [wav](https://drive.google.com/file/d/19eQyATSxJB1Ia6eBBTHaz1OycsbAL0qM/view?usp=sharing) |
| Pop | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_0.50_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_0.50_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_0.50_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_0.50_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_0.50_HP.wav)
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1y8MFOQ4uEhs_S2V_FpPHfPeLCOpfdLAa/view?usp=sharing) | [wav](https://drive.google.com/file/d/1E6SlzID07ZmHOLE_GW3Dz3HizmnMf13U/view?usp=sharing) | [wav](https://drive.google.com/file/d/1pDcNsUyzGP3yr_TA7G7vJzBRi6bHuuTL/view?usp=sharing) | [wav](https://drive.google.com/file/d/1fbkMupHp8PTXIg6_QINDTyBWkfnzO7DA/view?usp=sharing) | [wav](https://drive.google.com/file/d/1lnP-75-QsIwXXfqsXqKPN6z4Qs4s_AWc/view?usp=sharing) |
| SingingVoice | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_0.50_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_0.50_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_0.50_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_0.50_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_0.50_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1pzzm1xBB4Qo-vcAdrxDSHiec4CWPpds8/view?usp=sharing) | [wav](https://drive.google.com/file/d/1Oq-CiDbw4i20RoSqsx8YMDvq3p_TV06x/view?usp=sharing) | [wav](https://drive.google.com/file/d/10eh-jad5_VhCqiR6F_irK5jXp0rlq2ay/view?usp=sharing) | [wav](https://drive.google.com/file/d/1iAgToNlK7LMFA-VVMlB3O_hPiChJZN34/view?usp=sharing) | [wav](https://drive.google.com/file/d/1LUHXGkYc-4IBpuM0DiQn_pBGS30-hFMR/view?usp=sharing) |

### Stretching factor α=1.2

| Name | Method | Original | OLA | WSOLA | Phase Vocoder | Phase Vocoder (phase locking) | TSM based on HPSS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| CastanetsViolin | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.20_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.20_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.20_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.20_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.20_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1o7BtVNyZ9IYF5Jf6llwoMtFMYpzc9Idj/view?usp=sharing) | [wav](https://drive.google.com/file/d/1IDS4TjmhE3Ge2lD_xbN8Flw508ta_OV7/view?usp=sharing) | [wav](https://drive.google.com/file/d/1rMjZcG4Izrlc9_cHdN96KP6EwdgwsLg4/view?usp=sharing) | [wav](https://drive.google.com/file/d/1GMEYrePkNejHEBE9n0DyTnnjiEpUm3wi/view?usp=sharing) | [wav](https://drive.google.com/file/d/1QMRE7Qo5SuCgqhHSz6_DZWWWS-joh3T4/view?usp=sharing) |
| DrumSolo | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.20_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.20_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.20_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.20_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.20_HP.wav)
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1YgqwREMoOfSf2VPXLkzLNewKFlJ0iqmR/view?usp=sharing) | [wav](https://drive.google.com/file/d/1ZT-v8x65uRnhTRf9us8NI3NuoO8ia3m7/view?usp=sharing) | [wav](https://drive.google.com/file/d/1uGB4L5ffzwew7aeEqT1Yu1HGIXemupWc/view?usp=sharing) | [wav](https://drive.google.com/file/d/13k8CEktMpkRrrUSKnrVONqM8_yI1SysC/view?usp=sharing) | [wav](https://drive.google.com/file/d/1uozKTawYC9i8f5jbD4SoQjxh4PhjL-i8/view?usp=sharing) |
| Pop | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.20_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.20_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.20_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.20_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.20_HP.wav)
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1gj3PpiMR7OMPrRDej9Z-oxRf0b-ik-Gf/view?usp=sharing) | [wav](https://drive.google.com/file/d/1GKCkZU2dOVTk6ImDfEf3Gf3PrZxcReHW/view?usp=sharing) | [wav](https://drive.google.com/file/d/19Y02rGU6YEzAHtvSfpdHtBvlda8EGQZ6/view?usp=sharing) | [wav](https://drive.google.com/file/d/1yVye1wHpxeuCXOAZaVfWOC4G6xL4H_Hu/view?usp=sharing) | [wav](https://drive.google.com/file/d/1qfRglRBEzQDwI3iXhb-2RdNkYULJnNQC/view?usp=sharing) |
| SingingVoice | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.20_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.20_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.20_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.20_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.20_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1IxMpXjuBzrVbofo8FMMbkOREZkaW17bQ/view?usp=sharing) | [wav](https://drive.google.com/file/d/1iXpWEIKKHTkx0VCTxtXbhAIyxVO5CLme/view?usp=sharing) | [wav](https://drive.google.com/file/d/1XH_5sfZLSDgziXEbK_ApltScGVS0EVHT/view?usp=sharing) | [wav](https://drive.google.com/file/d/1sgBpTOz_WYVc8iDTQyjxmzHZYhgu0elS/view?usp=sharing) | [wav](https://drive.google.com/file/d/1eT9yKW-LTfifjr0C8Y1X4DghLLNXsz4W/view?usp=sharing) |

### Stretching factor α=1.8

| Name | Method | Original | OLA | WSOLA | Phase Vocoder | Phase Vocoder (phase locking) | TSM based on HPSS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| CastanetsViolin | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.80_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.80_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.80_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.80_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/CastanetsViolin_1.80_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/14pwBV64ycLHdBUgGbpNm0qfL_asIwlIK/view?usp=sharing) | [wav](https://drive.google.com/file/d/1IBRwYsBHaTOTfdUFZuOvGhvsSJOy4TwA/view?usp=sharing) | [wav](https://drive.google.com/file/d/1Rkw1Gg83_7t8bMZ4uO2PTalP8PexMsZH/view?usp=sharing) | [wav](https://drive.google.com/file/d/1aaEHj4dhpxiruesUXGmtNqz5ar-H7jkx/view?usp=sharing) | [wav](https://drive.google.com/file/d/15u0ToohxKpIYnelO0RlKsLv0CTqamIiZ/view?usp=sharing) |
| DrumSolo | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.80_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.80_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.80_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.80_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/DrumSolo_1.80_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1h1AGHMz1z1rkg8bRV94lBq1h-7tPg2N2/view?usp=sharing) | [wav](https://drive.google.com/file/d/12KlsY0Et0MICm4F3aFPUqkWGPRsKG8W0/view?usp=sharing) | [wav](https://drive.google.com/file/d/1ZNWoYTr_ErXXcq2bFU3o2YuqhTelZ1Q7/view?usp=sharing) | [wav](https://drive.google.com/file/d/1AZMGWQ9GzqeQA-wIMCyfvDNW4ji-tZsR/view?usp=sharing) | [wav](https://drive.google.com/file/d/139lVGzUwyrSo9AcRp3kuDQABiHcnKcxn/view?usp=sharing) |
| Pop | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.80_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.80_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.80_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.80_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/Pop_1.80_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1vxFD5Cj6wS6_tj66DPMmFQfg2JLxgI3j/view?usp=sharing) | [wav](https://drive.google.com/file/d/1BiNkuTmBn_HJAbBLCim8BP3Q7qPAIUzT/view?usp=sharing) | [wav](https://drive.google.com/file/d/1f4dZc51EgIudt8MoCQDvwtbkoTk6svb9/view?usp=sharing) | [wav](https://drive.google.com/file/d/1aPs4ufHBxyahOgPAVj3CbDdEW4elRj85/view?usp=sharing) | [wav](https://drive.google.com/file/d/1mhwNUVUYK2lFIqR8o657uG7wb60b3IWZ/view?usp=sharing) |
| SingingVoice | TSM Toolbox | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_ORIG.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.80_OLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.80_WSOLA.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.80_PV.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.80_PVpl.wav) | [wav](https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/SingingVoice_1.80_HP.wav) |
| - | PyTSMod | - | [wav](https://drive.google.com/file/d/1HCJwXaHCnACFTCW-Q8lN40N4Oxr-jfmD/view?usp=sharing) | [wav](https://drive.google.com/file/d/1vZ54pQusHWRJs9fggpTOq02vGNTY5bI5/view?usp=sharing) | [wav](https://drive.google.com/file/d/1TP2ZoV028tqFrILhCZmnYvflY-YdM3Bd/view?usp=sharing) | [wav](https://drive.google.com/file/d/1EQotSRP2rma3i1XioJW0998HJLiq_jQV/view?usp=sharing) | [wav](https://drive.google.com/file/d/1npTbI0sjKOEUifSXQbAqluxGRtG0O4t7/view?usp=sharing) |

## References

[1] Jonathan Driedger, Meinard Müller. "TSM Toolbox: MATLAB Implementations of Time-Scale Modification Algorithms", *Proceedings of the 17th International Conference on Digital Audio Effects (DAFx-14).* 2014.

[2] Jonathan Driedger, Meinard Müller. "A review of time-scale modification of music signals", *Applied Sciences, 6(2), 57.* 2016.

[3] Udo Zölzer. "DAFX: digital audio effects", *John Wiley & Sons.* 2011.

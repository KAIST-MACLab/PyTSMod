# PyTSMod

[![PyPI](https://img.shields.io/pypi/v/pytsmod.svg)](https://pypi.python.org/pypi/pytsmod)
[![Build Status](https://img.shields.io/github/workflow/status/KAIST-MACLab/PyTSMod/Python%20package)](https://github.com/KAIST-MACLab/PyTSMod/actions/workflows/python-package.yml)
![Python](https://img.shields.io/pypi/pyversions/pytsmod.svg)
![license](https://img.shields.io/github/license/KAIST-MACLab/PyTSMod.svg)
![downloads](https://img.shields.io/pypi/dm/pytsmod.svg)

PyTSMod is an open-source library for Time-Scale Modification algorithms in Python 3. PyTSMod contains basic TSM algorithms such as Overlap-Add (OLA), Waveform-Similarity Overlap-Add (WSOLA), Time-Domain Pitch-Synchronous Overlap-Add (TD-PSOLA), and Phase Vocoder (PV-TSM). We are also planning to add more TSM algorithms and pitch shifting algorithms.

Full documentation is available on <https://pytsmod.readthedocs.io>

![open-issues](https://img.shields.io/github/issues/KAIST-MACLab/pytsmod.svg)
![closed-issues](https://img.shields.io/github/issues-closed/KAIST-MACLab/pytsmod.svg)
![open-prs](https://img.shields.io/github/issues-pr/KAIST-MACLab/pytsmod.svg)
![closed-prs](https://img.shields.io/github/issues-pr-closed/KAIST-MACLab/pytsmod.svg)

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

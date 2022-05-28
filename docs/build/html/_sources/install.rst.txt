Installation
************

PyPI
~~~~
PyTSMod is hosted on PyPI. To install, run the following command in your Python environment::

$ pip install pytsmod

Build with Poetry
~~~~~~~~~~~~~~~~~
To build the package manually from the `release archive <https://github.com/KAIST-MACLAb/PyTSMod/releases>`_ or repo, `Poetry <https://python-poetry.org>`_ is needed. After install Poetry, build wheel file with the following command::

$ poetry build

After build the package, you can install through pip::

$ pip install dist/NAME_OF_PACKAGE.whl

Requirements
~~~~~~~~~~~~
To use PyTSMod, Python with version >= 3.8 and following packages are required.

- Numpy (>=1.20.0)
- Scipy (>=1.8.0)
- soundfile (>=0.10.0)
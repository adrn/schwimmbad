.. _install:

************
Installation
************

.. image:: http://img.shields.io/pypi/v/schwimmbad.svg?style=flat
        :target: https://pypi.python.org/pypi/schwimmbad/

Dependencies
============

For running in serial, or using Python's built-in `multiprocessing` module,
`schwimmbad` has no third-party dependencies.
To run with MPI, you must have a compiled MPI library (e.g., `OpenMPI
<https://www.open-mpi.org/>`_) and ``mpi4py``.
To run with joblib, you must have ``joblib`` installed.
Each of these dependencies is either ``pip`` or ``conda`` installable.

With `conda`
============

To install with `conda <http://continuum.io/downloads>`_, use the
`conda-forge <https://conda-forge.github.io/>`_ channel::

    conda install -c conda-forge schwimmbad

With `pip`
==========

To install the latest stable version using ``pip``, use::

    pip install schwimmbad

To install the development version::

    pip install git+https://github.com/adrn/schwimmbad

From source
===========

The latest development version can be cloned from
`GitHub <https://github.com/>`_ using ``git``::

   git clone git://github.com/adrn/schwimmbad.git

To install the project (from the root of the source tree, e.g., inside
the cloned ``schwimmbad`` directory)::

    python setup.py install


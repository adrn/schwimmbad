The Schwimmbad
==============

.. image:: https://travis-ci.org/adrn/schwimmbad.svg?branch=master
    :target: https://travis-ci.org/adrn/schwimmbad

.. image:: http://img.shields.io/pypi/v/schwimmbad.svg?style=flat
    :target: https://pypi.python.org/pypi/schwimmbad/

.. image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
    :target: https://github.com/adrn/schwimmbad/blob/master/LICENSE

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.885577.svg
    :target: https://zenodo.org/record/885577#.Wa9WVBZSy2w

.. image:: http://joss.theoj.org/papers/10.21105/joss.00357/status.svg
    :target: http://dx.doi.org/10.21105/joss.00357

``schwimmbad`` provides a uniform interface to parallel processing pools
and enables switching easily between local development (e.g., serial processing
or with ``multiprocessing``) and deployment on a cluster or supercomputer
(via, e.g., MPI or JobLib).

Installation
------------

The easiest way to install is via `pip`::

    pip install schwimmbad

See the `installation
instructions <http://schwimmbad.readthedocs.io/en/latest/install.html>`_ in the
`documentation <http://schwimmbad.readthedocs.io>`_ for more information.

Documentation
-------------

.. image:: https://readthedocs.org/projects/schwimmbad/badge/?version=latest
    :target: http://schwimmbad.readthedocs.io/en/latest/?badge=latest

The documentation for ``schwimmbad`` is hosted on `Read the docs
<http://schwimmbad.readthedocs.io/>`_.

Attribution
-----------

If you use this software in a scientific publication, please cite the `JOSS
<http://joss.theoj.org/>`_ article:

.. code-block:: tex

    @article{schwimmbad,
      doi = {10.21105/joss.00357},
      url = {https://doi.org/10.21105/joss.00357},
      year  = {2017},
      month = {sep},
      publisher = {The Open Journal},
      volume = {2},
      number = {17},
      author = {Adrian M. Price-Whelan and Daniel Foreman-Mackey},
      title = {schwimmbad: A uniform interface to parallel processing pools in Python},
      journal = {The Journal of Open Source Software}
    }

License
-------

Copyright 2016-2017 Adrian Price-Whelan and contributors.

schwimmbad is free software made available under the MIT License. For details
see the LICENSE file.

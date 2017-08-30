.. schwimmbad documentation master file, created by
   sphinx-quickstart on Tue Aug  1 15:54:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**************
The Schwimmbad
**************

.. image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
    :target: https://github.com/adrn/schwimmbad/blob/master/LICENSE

``schwimmbad`` provides a uniform interface to parallel processing pools
and enables switching easily between local development (e.g., serial processing
or with :py:mod:`multiprocessing`) and deployment on a cluster or supercomputer
(via, e.g., MPI or JobLib).

.. toctree::
    :maxdepth: 1

    install
    contributing

Getting started
===============

The utilities provided by ``schwimmbad`` require that your tasks or data can be
"chunked" and your code can be "mapped" onto the chunked tasks. For example, the
very common use-case of executing the same function or code on every datum in
a large data set::

    data = list(range(10000))

    def do_the_processing(x):
        # Do something with each value in the data set!
        # For example, here we just square each value
        return x**2

    values = []
    for x in data:
        values.append(do_the_processing(x))

In the example above, instead of looping over each item in ``data``, we could
have equally well used the Python built-in :func:`map` function::

    values = list(map(do_the_processing, data))

This applies the function (passed as the first argument) to each element in the
iterable (second argument). In Python 3, :func:`map` returns a generator object,
so we call :class:`list` on this to get out the values.

The above :func:`map` example executes the function in *serial* over each
element in ``data``. That is, it just goes one by one through the ``data``
object, executes the function, returns, and carries on, all on the same
processor core. If we can write our code in this style (using :func:`map`), we
can easily swap in the ``Pool`` classes provided by ``schwimmbad`` to allow us
to switch between various parallel processing frameworks. The easiest to
understand is the :class:`~schwimmbad.SerialPool`, as this is just a
class-based wrapper of the built-in (serial) :func:`map` function. The same
example above can be run with :class:`~schwimmbad.SerialPool` by doing::

    from schwimmbad import SerialPool

    pool = SerialPool()
    values = list(pool.map(do_the_processing, data))

The only difference here is we call the ``.map()`` *method* of the instantiated
``Pool`` class.

If we wanted to switch to using multiprocessing, using, for example, the Python
built-in :mod:`multiprocessing` package to utilize multiple cores on the same
processor, we can just swap out the pool definition to instead use the
:class:`~schwimmbad.MultiPool` class::

    from schwimmbad import MultiPool

    with MultiPool() as pool:
        values = list(pool.map(do_the_processing, data))

Note that the core processing line (``values = ...``) looks identical to the
above, but we've only changed the definition of the ``pool`` object. In detail,
we're now using a `context manager
<https://en.wikibooks.org/wiki/Python_Programming/Context_Managers>`_ (using a
Python ``with`` statement) to handle creating and *closing* the multiprocessing
pool. With the exception of the :class:`~schwimmbad.SerialPool`, all
other pool classes need to be explicity closed after processing. We could have
also written::

    pool = MultiPool()
    values = list(pool.map(do_the_processing, data))
    pool.close()

See the examples listed below for demonstrations of using the
:class:`~schwimmbad.MPIPool` and :class:`~schwimmbad.JoblibPool`.

Examples
--------

.. toctree::
    :maxdepth: 2

    examples/index

API documentation
=================

.. toctree::
    :maxdepth: 1

    api

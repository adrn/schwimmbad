---
title: 'schwimmbad: A uniform interface to parallel processing pools in Python'
tags:
  - Python
  - multiprocessing
  - parallel computing
authors:
  - name: Adrian M. Price-Whelan
    orcid: 0000-0003-0872-7098
    affiliation: 1
  - name: Daniel Foreman-Mackey
    orcid: 0000-0002-9328-5652
    affiliation: 2
affiliations:
 - name: Lyman Spitzer, Jr. Fellow, Princeton University
   index: 1
 - name: Sagan Fellow, University of Washington
   index: 2
date: 11 August 2017
bibliography: paper.bib
---

# Summary

Many scientific and computing problems require doing some calculation on all
elements of some data set. If the calculations can be executed in parallel
(i.e. without any communication between calculations), these problems are said
to be [*perfectly
parallel*](https://en.wikipedia.org/wiki/Embarrassingly_parallel). On computers
with multiple processing cores, these tasks can be distributed and executed in
parallel to greatly improve performance. A common paradigm for handling these
distributed computing problems is to use a processing "pool": the "tasks" (the
data) are passed in bulk to the pool, and the pool handles distributing the
tasks to a number of worker processes when available.

In Python, the built-in ``multiprocessing`` package provides a ``Pool`` class
for exactly this design case, but only supports distributing the tasks amongst
multiple cores of a single processor. To extend to large cluster computing
environments, other protocols are required, such as the Message Passing
Interface [MPI; @Forum1994]. ``schwimmbad`` provides new ``Pool`` classes for a
number of parallel processing environments with a consistent interface. This
enables easily switching between local development (e.g., serial processing
or with Python's built-in ``multiprocessing``) and deployment on a cluster or
supercomputer (via, e.g., MPI or JobLib). This library supports processing pools
with a number of backends:

* Serial processing: ``SerialPool``
* ``Python`` standard-library ``multiprocessing``: ``MultiPool``
* [``OpenMPI``](open-mpi.org) [@Gabriel2004] and
  [``mpich2``](https://www.mpich.org/) [@Lusk1996] via the ``mpi4py``
  package [@Dalcin2005; @Dalcin2008]: ``MPIPool``
* [``joblib``](http://pythonhosted.org/joblib/): ``JoblibPool``

All pool classes provide a ``.map()`` method to distribute tasks to a specified
worker function (or callable), and support specifying a callback function that
is executed on the master process to enable post-processing or caching the
results as they are delivered.

# References

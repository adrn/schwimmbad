---
title: 'schwimmbad: A uniform API to parallel processing pools in Python'
tags:
  - Python
  - multiprocessing
  - parallel computing
authors:
  - name: Adrian Price-Whelan
    orcid: 0000-0003-0872-7098
    affiliation: Lyman Spitzer, Jr. Fellow, Princeton University
  - name: Daniel Foreman-Mackey
    orcid: 0000-0002-9328-5652
    affiliation: Sagan Fellow, University of Washington
date: XX August 2017
bibliography: paper.bib
---

# Summary

``schwimmbad`` provides a uniform interface to parallel processing pools
and enables switching easily between local development (e.g., serial processing
or with Python's built-in `multiprocessing`) and deployment on a cluster or
supercomputer (via, e.g., MPI or JobLib). This library supports processing pools
with a number of backends:

* Serial processing: ``SerialPool``
* ``Python`` standard-library ``multiprocessing``: ``MultiPool``
* [``OpenMPI``](open-mpi.org) (Gabriel et al. 2004) and
  [``mpich2``](https://www.mpich.org/) via the ``mpi4py`` package (Dalcin et al.
  2005, 2008): ``MPIPool``
* [``joblib``](http://pythonhosted.org/joblib/): ``JoblibPool``

All pool classes provide a ``.map()`` method to distribute tasks to a specified
worker function (or callable), and support specifying a callback function that
is executed on the master process to enable post-processing or caching the
results as they are delivered.

# References

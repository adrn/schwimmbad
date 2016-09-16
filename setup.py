#! /usr/bin/env python

# Release to pypi with:
# python setup.py sdist upload

# Standard library
import sys
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Thanks DFM:
# Handle encoding
major, minor1, minor2, release, serial = sys.version_info
if major >= 3:
    def rd(filename):
        f = open(filename, encoding="utf-8")
        r = f.read()
        f.close()
        return r
else:
    def rd(filename):
        f = open(filename)
        r = f.read()
        f.close()
        return r

vre = re.compile("__version__ = \"(.*?)\"")
m = rd(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "schwimmbad", "__init__.py"))
version = vre.findall(m)[0]

setup(
    name="schwimmbad",
    version=version,
    author="Adrian Price-Whelan",
    author_email="adrn@princeton.edu",
    packages=["schwimmbad", "schwimmbad.tests"],
    url="https://github.com/adrn/schwimmbad",
    license="MIT",
    description="A common interface for parallel processing pools.",
    long_description=rd("README.md"),
    package_data={"": ["LICENSE"]},
    include_package_data=True,
    install_requires=["six"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)

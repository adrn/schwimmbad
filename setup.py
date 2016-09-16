#! /usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="schwimmbad",
    version='v0.1',
    author="Adrian Price-Whelan",
    author_email="adrn@princeton.edu",
    packages=["schwimmbad"],
    url="https://github.com/adrn/schwimmbad",
    license="MIT",
    description="A common interface for multiprocessing pools.",
    long_description="",
    package_data={"": ["LICENSE"]},
    include_package_data=True,
    install_requires=["six"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)

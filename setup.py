#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="precisionapi",
    packages=find_packages(),
    version="0.1.1",
    install_requires=["requests","attrs"],
)

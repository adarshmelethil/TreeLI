#!/usr/bin/env python

from setuptools import setup


setup(
    name="TreeLI",
    version="0.1",
    description="CLI tool",
    url="https://github.com/adarshmelethil/TreeLI",
    author="Adarsh Melethil",
    author_email="adarshmelehtil@gmail.com",
    packages=["treeli", "treeli.tests"],

    install_requires=['attrs'],
    extras_require={
        'dev': ["pytest"],
    },
)

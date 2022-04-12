from setuptools import setup
import os
import sys

PKG_NAME = "StarbucksAutoma"

setup(
    name=PKG_NAME,
    version="1.0",
    description=("Starbucks auto schdeuler written in Python"),
    author="Jared Dyreson",
    author_email="jareddyreson@csu.fullerton.edu",
    url="https://github.com/JaredDyreson/starbucks_automa_production",
    license="GNU GPL-3.0",
    packages=[PKG_NAME],
    dependency_links=["https://github.com/JaredDyreson/sudo_execute.git"],
    install_requires=[
        "google_auth_oauthlib",
        "google-api-python-client",
        "termcolor",
        "selenium",
    ],
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3.8"],
)

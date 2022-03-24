from setuptools import setup
import os
import sys

PKG_NAME = "StarbucksAutoma"

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, "README.md")) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, PKG_NAME, "version.py")) as f:
    exec(f.read(), version)

setup(
    name=PKG_NAME,
    version=version["__version__"],
    description=("Starbucks auto schdeuler written in Python"),
    long_description=long_description,
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

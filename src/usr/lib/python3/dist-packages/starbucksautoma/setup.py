#!/usr/bin/env python3.5

from distutils.core import setup

setup(
	name='starbucksautoma',
	version='1.0',
	description='Automatic work scheduler for the Starbucks Partner Portal',
	author='Jared Dyreson',
	author_email='jared.dyreson@gmail.com',
	url='https://github.com/JaredDyreson/starbucks_automa_production/',
	install_requires=['google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'selenium', 'beautifulsoup4']
)



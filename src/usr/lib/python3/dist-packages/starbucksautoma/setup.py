#!/usr/bin/env python3.5

from distutils.core import setup
import json

setup(
	name='starbucksautoma',
	version='1.0',
	description='Automatic work scheduler for the Starbucks Partner Portal',
	author='Jared Dyreson',
	author_email='jared.dyreson@gmail.com',
	url='https://github.com/JaredDyreson/starbucks_automa_production/',
	install_requires=['google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'selenium', 'beautifulsoup4']
)

def gen_credentials_json():
	body = {
		"username": "",
		"password": "",
		"name": "",
		"hobby": "",
		"hometown": "",
		"timezone": "",
		"store_location": ""
	}
	with open("config.json", "w+") as f:
		f.write(json.dumps(body))	

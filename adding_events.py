#!/usr/bin/env python3.5

#
# Copyright 2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# http://www.apache.org/licenses/LICENSE-2.0
# You may obtain a copy of the License at
#
# distributed under the License is distributed on an "AS IS" BASIS,
# Unless required by applicable law or agreed to in writing, software
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# NOTES

# [START calendar_quickstart], hacked with love -> Jay


# checking if event is already in the calendar --> https://stackoverflow.com/questions/55272913/how-to-check-google-calendar-to-see-if-event-already-exists-before-adding
# also was a good idea to abstract this to a class ^ 
# using the freebusy API call --> https://gist.github.com/cwurld/9b4e10dbeecab28345a3


from __future__ import print_function
from datetime import datetime
import pickle
from googleapiclient.discovery import build
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from pprint import pprint as pp
import getpass
from starbucksautoma import time_struct as ts
import re
from datetime import timedelta
from starbucksautoma import time_struct

from starbucksautoma import json_parser as jp
from termcolor import colored
# If modifying these scopes, delete the file token.pickle.

SCOPES = ['https://www.googleapis.com/auth/calendar']
parser = jp.jsonparser("/home/jared/Applications/starbucks_automa/credentials/config.json")



class GoogleEventHandler():
	def __init__(self):
		self.credentials = self.gen_credentials()
		self.service = build('calendar', 'v3', credentials=self.gen_credentials())
	def gen_credentials(self):
		location = str("/home/{}/Applications/starbucks_automa/credentials".format(getpass.getuser())) 
		credentials = None
		if os.path.exists('{}/token.pickle'.format(location)):
			with open('{}/token.pickle'.format(location), 'rb') as token:
				credentials = pickle.load(token)
			if not credentials or not credentials.valid:
				if credentials and credentials.expired and credentials.refresh_token:
					credentials.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('{}/credentials.json'.format(location), SCOPES)
			credentials = flow.run_local_server()
		with open('{}/token.pickle'.format(location), 'wb') as token:
			pickle.dump(credentials, token)
		return credentials
	def get_events(self):
		now = datetime.utcnow().isoformat()+'Z'
		return self.service.events().list(calendarId='primary', timeMin=now, maxResults=50, singleEvents=True, orderBy='startTime').execute().get('items', [])
	def get_free_busy(self, event: time_struct, calendar_id='primary', timezone=parser.getjsonkey(key="timezone")):
		# NOTE
		# FALSE: you are free
		# TRUE: you are busy
		copy = event.end
		event.end+=timedelta(hours=2)
		base_ = event.google_calendar_format()
		event.end = copy
		start = base_[0]
		end = base_[1]
		request_body = {
			"timeMin": start,
			"timeMax": end,
			"timeZone": timezone,
			"items": [{"id": calendar_id}]
		}
		freebusy_result_ = self.service.freebusy().query(body=request_body).execute()
		freebusy_result_list_ = freebusy_result_['calendars'][calendar_id]['busy']
		if(len(freebusy_result_list_) == 0):
			return False
		else:
			for event_element_ in freebusy_result_list_:
				if(event_element_ is not None):
					check_event = time_struct.time_struct.from_dict(event_element_)
					if(check_event.form_submit_body() == event.form_submit_body()):
						return True
		return False
	def add_event(self, event: time_struct):
		# add an event to the Google Calendar
		json_complient_event = json.loads(event.form_submit_body())
		if(not self.get_free_busy(event)):
			self.service.events().insert(calendarId='primary', body=json_complient_event).execute()
			success_message_ = "[+] Sucessfully added event {}".format(event.google_date_added_string())
			print(colored(success_message_, 'green', 'on_grey'))
		else:
			duplicate_event_message_ = "[-] Event {} is already in the calendar".format(event.google_date_added_string())
			print(colored(duplicate_event_message_, 'red', 'on_grey'))

def assert_test():
	# this code needs to be manually changed if run at a later date
	bot = GoogleEventHandler()

	birthday_str = "4/28/2020 08:00:00"
	birthday_time_ = datetime.strptime(birthday_str, "%m/%d/%Y %H:%M:%S")
	birthday_time_end = (birthday_time_+timedelta(hours=1, minutes=50))
	birthday_structure = time_struct.time_struct(birthday_time_, birthday_time_end)

	example_work_day_event = "07/25/2019 02:30:00"
	example_work_day_time_start_ = datetime.strptime(example_work_day_event, "%m/%d/%Y %H:%M:%S")
	example_work_day_time_end_ = (example_work_day_time_start_+timedelta(hours=1, minutes=50))
	add_to_calendar = time_struct.time_struct(example_work_day_time_start_, example_work_day_time_end_)

	print("checking gen_credentials...")
	if(bot.gen_credentials() is not None):
		print("\t[+] passed")
	else:
		print("\t[-] failed")
	print("checking get_events function...")
	if(len(bot.get_events()) == 50):
		print("\t[+] passed")
	else:
		print("\t[-] failed")
		print("size of: {}".format(len(bot.get_events())))
	
	print("testing free busy....")
	if (bot.get_free_busy(birthday_structure)):
		print("\t[+] passed")
	else:
		print("\t[-] failed")
	print("testing adding event to calendar")
	bot.add_event(add_to_calendar)

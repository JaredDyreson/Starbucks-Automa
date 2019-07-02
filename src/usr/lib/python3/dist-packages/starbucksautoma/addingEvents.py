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
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.

SCOPES = ['https://www.googleapis.com/auth/calendar']



class GoogleEventHandler():
        def __init__(self):
                self.credentials = self.gen_credentials()
                self.service = build('calendar', 'v3', credentials=self.gen_credentials())
        def gen_credentials(self):
                location = str("/home/{}/Applications/starbucks_automa/credentials".format(getpass.getuser())) 
                credentials = None
                # The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time
                if os.path.exists('{}/token.pickle'.format(location)):
                        with open('{}/token.pickle'.format(location), 'rb') as token:
                                credentials = pickle.load(token)
                # If there are no (valid) credentials available, let the user log in.
                if not credentials or not credentials.valid:
                        if credentials and credentials.expired and credentials.refresh_token:
                                credentials.refresh(Request())
                        else:
                                flow = InstalledAppFlow.from_client_secrets_file('{}/credentials.json'.format(location), SCOPES)
                                credentials = flow.run_local_server()
                # Save the credentials for the next run
                        with open('{}/token.pickle'.format(location), 'wb') as token:
                                pickle.dump(credentials, token)
                return credentials

        def add_event(self, event):
                # add an event to the Google Calendar
                # also print the added date in human readable format
                event = json.loads(event)
                event_struct = self.gen_time_struct(event)
                if event_struct is not None:
                        # we want this format
                        # Monday January 1, 2019 from 15:45 to 18:00
                        begin_h = event_struct.gen_human_readable(event_struct.begin)
                        end_h = event_struct.gen_human_readable(event_struct.end)
                        if not (self.get_free_busy(event_struct.begin, event_struct.end)):
                                self.service.events().insert(calendarId='primary', body=event).execute()
                                print("[+] Successfully added event from {} to {}".format(begin_h, end_h.split()[3]))
                        else:
                                print("[-] Event from {} to {} is already in the calendar".format(begin_h, end_h.split()[3]))
        def get_events(self):
                now = datetime.utcnow().isoformat()+'Z'
                return self.service.events().list(calendarId='primary', timeMin=now, maxResults=50, singleEvents=True, orderBy='startTime').execute().get('items', [])
        def gen_time_struct(self, event):
                if (event.get('start').get('dateTime') is None) or (event.get('end').get('dateTime') is None):
                        return None
                ts_event = ts.time_struct()
                ts_event.summary = event.get('summary')
                ts_event.begin = event.get('start').get('dateTime').replace("-07:00", "")
                ts_event.end = event.get('end').get('dateTime').replace("-07:00", "")
                return ts_event

        def get_free_busy(self, start, end, calendar_id='primary', time_zone='America/Los_Angeles'):
                # FALSE -> You are not busy
                # TRUE -> You are busy

                # the way that freebusy works is that you cannot just specify the start and end time of the event, just use the start and add an hour to the end time, it should work from there
                start+="Z"
                end_temp = datetime.strptime(end, "%Y-%m-%d{}%H:%M:%S".format("T"))
                end_temp+=timedelta(days=1)
                end_temp_string = end_temp.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", "Z"))
                request_body = {
                        "timeMin": start,
                        "timeMax": end_temp_string,
                        "timeZone": time_zone,
                        "items": [{"id": calendar_id}]
                }
                freebusy_result = self.service.freebusy().query(body=request_body).execute()
                freebusy_result_list = freebusy_result['calendars'][calendar_id]['busy']
                # if the frebusy events list is empty then we are clearly free
                if (len(freebusy_result_list)) == 0:
                        return False
                else:
                        end_temp_way = end_temp
                        for result in freebusy_result_list:
                                end_temp = end_temp_way
                                end_temp-=timedelta(days=1)
                                end_temp_string = end_temp.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", "Z"))
                                e = result['end'].replace("-07:00", "Z").strip()
                                s = result['start'].strip()
                                start = start.replace("Z", "-07:00").strip()
                                if (s == start) and (e == end_temp_string):
                                        return True
                return False 
                        

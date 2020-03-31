#!/usr/bin/env python3.8

from datetime import datetime, timedelta
from starbucksautoma.adding_events import GoogleEventHandler
from starbucksautoma.time_struct import time_struct
from pprint import pprint as pp
import json

event_handler = GoogleEventHandler()
event_name = "Jared's Work"

def get_current_week() -> list:
  """
  Get the current week's days into isoformat.
  """
  week = []
  counter = 0
  today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
  # wind the week day back 
  while(today.weekday() != 0):
    counter+=1
    today = today - timedelta(days=1)
    week.append(today)
  # advance date to current
  today+=timedelta(days=counter)
  # get the rest of the days
  for x in range(counter, 7):
    week.append(today)
    today+=timedelta(days=1)
  return week

def get_work_day(current: datetime):
    next_day = '{}Z'.format((current+timedelta(days=1)).isoformat())
    current = '{}Z'.format(current.isoformat())
    return event_handler.service.events().list(calendarId='primary', timeMin=current, timeMax=next_day, maxResults=50, singleEvents=True, orderBy='startTime').execute().get('items', [])

def get_work_week(summary: str):
    work_week = []
    for day in get_current_week():
      response = get_work_day(day)
      for i, element in enumerate(response):
        summary = element['summary']
        start = element['start']['dateTime']
        end = element['end']['dateTime']
        event_id = element['id']
        if(summary == summary):
          work_day = {
            'summary': summary,
            'start': start,
            'end': end,
            'event_id': event_id
          }
          work_week.append(work_day)
    return work_week

def clear_work_week():
    for element in get_work_week(event_name):
        try:
          event_handler.service.events().delete(calendarId='primary', eventId=element['event_id']).execute()
        except Exception as error:
            print("got an error: {}".format(error))

def check_if_working(day: datetime, summary: str) -> bool:
    for element in get_work_day(day):
      if(element['summary'] == summary): return element['start']['dateTime'], element['end']['dateTime'], element['id'], True
    return None, None, None, False

"""
Check if the event is in the calendar or not
"""

def add_events(event: time_struct):
  start, end, event_id, status = check_if_working(event.begin.replace(hour=0, minute=0, second=0, microsecond=0), event.summary)
  original_ = time_struct.from_string(start, end, event.summary)
  if not(original_ == event):
    json_complient_event = json.loads(most_recent.form_submit_body())
    event_handler.service.events().insert(calendarId='primary', body=json_complient_event).execute()
    event_handler.service.events().delete(calendarId='primary', eventId=event_id).execute()


s = datetime.today().replace(hour=15, minute=0, second=0)
e = datetime.today().replace(hour=19, minute=0, second=0)

most_recent = time_struct(s, e, event_name)
add_events(most_recent)

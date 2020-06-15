#!/usr/bin/env python3.8

# fix the entire python script with this line if there are issues
# :set tabstop=2 shiftwidth=2 expandtab | retab  
import datetime
from datetime import timedelta
from datetime import timezone
import json
import time
import collections
from StarbucksAutoma import json_parser as jp
import pytz
import getpass

from pprint import pprint as pp

username_ = getpass.getuser()


parser = jp.jsonparser("/home/{}/Applications/starbucks_automa/credentials/config.json".format(username_))

class time_struct(object):

    # start: datetime
    # end: datetime
    
    # constructors

    def __init__(self, start=datetime.datetime.today(), end=datetime.datetime.today(), summary="{}'s Work".format(parser.getjsonkey(key="name"))):
        self.begin = start
        self.end = end
        self.summary = summary

    @classmethod
    def from_string(cls, s: str, e: str, summary: str):
        s = datetime.datetime.strptime(s[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        e = datetime.datetime.strptime(e[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        return cls(s, e, summary) 

    @classmethod
    # get start and end from a dictionary/json responses but neglecting the summary tag
    def from_dict(cls, body: dict):
        # this function is broken because of daylight savings. figure out how this should work
        return self.from_string(body['start'], body['end'], body['summary'])
        # s = datetime.datetime.strptime(body['start'][:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        # e = datetime.datetime.strptime(body['end'][:19], "%Y-%m-%d{}%H:%M:%S".format("T"))

        # return cls(s, e)
    @classmethod
    # get start and end from a dictionary/json response including the summary to allow for comparing results from free busy
    def from_freebusy(cls, response: dict):
        b = str(response['start']['dateTime'])
        t = str(response['end']['dateTime'])

        s = datetime.datetime.strptime(b[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        e = datetime.datetime.strptime(t[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))

        summary = response['summary']
        return cls(s, e, summary)
    def __eq__(self, other):
        # check if the json event data is the same
        # return: boolean
        return self.form_submit_body() == other.form_submit_body()

    def __ne__(self, other):
        # return the inverse of the __eq__ operator
        # boolean
        return not self.__eq__(self, other)

    def __hash__(self):
        # dir(self): returns all of the possible attributes of this class
        # returns: hash of time_struct class
        return hash(",".join(dir(self)))

    def __repr__(self):
        return "Summary: {}\nStart: {}\nEnd: {}".format(
                self.summary,
                self.gen_human_readable(self.begin),
                self.gen_human_readable(self.end)
            )


    def is_midnight(self, time_object: datetime.datetime.time):
        # takes in either self.begin or self.end and returns boolean
        return datetime.time(0, 0) == time_object
    def google_calendar_format(self):
        # returns a list of string objects (len of 2) that can be passed to form_submit_body

        s = self.begin.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset(self.begin)))
        e = self.end.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset(self.end)))

        return [s, e]
    def get_time_elapsed(self):
        # compute total time working
        # return: float
        return abs(float((self.end - self.begin).total_seconds()/3600))
        
    def form_submit_body(self, timezone=parser.getjsonkey(key="timezone"), location=parser.getjsonkey(key="store_location")):
        # return a json body that will be used for submitting to the Google Calendar API
        # return : string representation of a json object
        body = [
            ('summary', "{}'s Work".format(parser.getjsonkey(key="name"))),
            ('start', {'dateTime': self.google_calendar_format()[0], 'timeZone': timezone}),
            ('end', {'dateTime': self.google_calendar_format()[1], 'timeZone': timezone}),
            ('location', location)
            ]
        final_submit_body = collections.OrderedDict(body)
        return json.dumps(final_submit_body, indent=4)

    def get_utc_offset(self, time_obj : datetime):
        # get the current UTC offset from your predetermined time zone RELATIVE TO THE DATE
        # returns in the regex format of : [0-9]{2}\:[0-9]{2}

        time_zone = parser.getjsonkey(key="timezone")

        current_offset = pytz.timezone(time_zone).localize(time_obj).strftime('%z')
        curret_offset = "{}:{}".format(current_offset[:3], current_offset[3:])

        return current_offset

    def gen_human_readable(self, time_obj: datetime):
        # return a date string that looks something like this: Monday January 2, 15:30

        string_version = datetime.datetime.strftime(time_obj, "%Y-%m-%d{}%H:%M:%S").format("T")
        return datetime.datetime.strptime(string_version, "%Y-%m-%d{}%H:%M:%S".format("T")).strftime("%A %B %d, %H:%M")

    def google_date_added_string(self):
        # return a string that can be used for reporting if an event has been added or is already present
        # example: from Monday January 2 11:15 to 15:15

        begin_h = self.gen_human_readable(self.begin)
        end_h = self.gen_human_readable(self.end)
        return "from {} to {}".format(begin_h, end_h.split()[3])
    def is_dst(self, time_obj : datetime):
        # returns true if the date is not rollback
        return datetime.datetime(2020, 3, 10) != time_obj.date()

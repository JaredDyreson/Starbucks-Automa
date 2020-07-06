#!/usr/bin/env python3.8


# from StarbucksAutoma.initialize import initializer
from StarbucksAutoma.json_parser import jsonparser

from datetime import datetime

import collections
import json
import pytz
import os
import pathlib


application_path = pathlib.Path(
    "/etc/StarbucksAutoma/credentials/config.json"
)


# initialize = initializer()
# if(not os.path.exists(application_path)):
    # initialize.make_user_config()
parser = jsonparser(initialize.read_contents())

current = datetime.today()
global_summary = "{}'s Work".format(parser.getjsonkey("name"))


class event_packet(object):
    def __init__(self, start : datetime, end: datetime, 
                    summary = global_summary):
        if not(isinstance(start, datetime) and
               isinstance(end, datetime) and
               isinstance(summary, str)):

               raise ValueError

        self.begin = start
        self.end = end
        self.summary = summary

    @classmethod
    def from_string(cls, s: str, e: str, summary: str):
        if not(isinstance(s, str) and
               isinstance(e, str) and
               isinstance(summary, str)):
               raise ValueError

        s = datetime.strptime(s[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        e = datetime.strptime(e[:19], "%Y-%m-%d{}%H:%M:%S".format("T"))
        return cls(s, e, summary)

    @classmethod
    def from_dict(cls, body: dict):
        """ Get start and end from a dictionary/json responses but neglecting the summary tag """

        if not(isinstance(body, dict)):
            raise ValueError
        return self.from_string(body['start'], body['end'], body['summary'])

    @classmethod
    def from_freebusy(cls, response: dict):
        """ Get start and end from a dictionary/json response including the summary to allow for comparing results from free busy """
        return self.from_string(response['start']['dateTime'], 
                                response['end']['dateTime'], response['summary'])

    def __eq__(self, other):
        """
        Check if the JSON event data is the same
        """

        return self.form_submit_body() == other.form_submit_body()

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def __hash__(self):
        return hash(",".join(dir(self)))

    def __repr__(self):
        return "Summary: {}\nStart: {}\nEnd: {}".format(
                self.summary,
                self.gen_human_readable(self.begin),
                self.gen_human_readable(self.end)
            )

    def is_midnight(self, time_object: datetime.time):
        """
        Checks if time event is midnight
        """

        return datetime.time(0, 0) == time_object

    def google_calendar_format(self):
        """
        Returns a list of string objects (len of 2) that can be passed to form_submit_body
        """

        s = self.begin.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset(self.begin)))
        e = self.end.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset(self.end)))

        return [s, e]

    def get_time_elapsed(self):
        """
        Compute total time working
        """

        return abs(float((self.end - self.begin).total_seconds()/3600))

    def form_submit_body(self):
        """
        Return a json body that will be used for submitting to the Google Calendar API
        """

        timezone, location = parser.getjsonkey("timezone"), parser.getjsonkey("location")

        body = [
            ('summary', global_summary,
            ('start', {'dateTime': self.google_calendar_format()[0], 'timeZone': timezone}),
            ('end', {'dateTime': self.google_calendar_format()[1], 'timeZone': timezone}),
            ('location', location)
            ]
        final_submit_body = collections.OrderedDict(body)
        return json.dumps(final_submit_body, indent=4)

    def get_utc_offset(self, time_obj: datetime):
        """
        Get the current UTC offset from your predetermined time zone RELATIVE TO THE DATE
        """

        time_zone = parser.getjsonkey(key="timezone")

        current_offset = pytz.timezone(time_zone).localize(time_obj).strftime('%z')
        return "{}:{}".format(current_offset[:3], current_offset[3:])

    def gen_human_readable(self, time_obj: datetime):
        """
        Return a date string that looks something like this: Monday January 2, 15:30
        """

        string_version = datetime.strftime(time_obj, "%Y-%m-%d{}%H:%M:%S").format("T")
        return datetime.strptime(string_version, "%Y-%m-%d{}%H:%M:%S".format("T")).strftime("%A %B %d, %H:%M")

    def google_date_added_string(self):
        """
        Return a string that can be used for reporting if an event has been added or is already present
        Example: from Monday January 2 11:15 to 15:15
        """

        begin_h = self.gen_human_readable(self.begin)
        end_h = self.gen_human_readable(self.end)
        return "from {} to {}".format(begin_h, end_h.split()[3])

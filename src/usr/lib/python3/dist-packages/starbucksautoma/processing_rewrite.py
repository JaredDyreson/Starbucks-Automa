#!/usr/bin/env python3.5
import time
import datetime
from datetime import timedelta
from datetime import timezone
import pytz
import json
import collections

class exportable_time_struct:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0


def formSubmittableJSON(s, e, timezone="America/Los_Angeles", location="15010 Imperial Hwy, La Mirada, CA 90638"):
    # USAGE: formSubmittableJSON(exportable_time_struct.start_time, exportable_time_struct.end_time)
    # also should be used in an iterative loop
    s = s.strftime("%Y-%m-%d %H:%M:%S%z").replace(" ", "T")
    e = e.strftime("%Y-%m-%d %H:%M:%S%z").replace(" ", "T")
    keyPair = [('summary', "Jared's Work"),
    ('start', {'dateTime': s, 'timeZone': timezone}),
    ('end', {'dateTime': e, 'timeZone': timezone}),
    ('location', location)]
    final = collections.OrderedDict(keyPair)
    return json.dumps(final, indent=4)

def get_time_elapsed(start, end):
        # USAGE
        # takes two datetime objects of isoformat and computes the difference in hours
        return int(time.mktime(end) - time.mktime(start)) / 3600 % 24

    

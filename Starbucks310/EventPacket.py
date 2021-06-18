#!/usr/bin/env python3.10

import json
import Time
import datetime
import collections


class EventPacket:
    def __init__(self, time: tuple[Time.Time], summary="Jared\'s Work"):
        if not(isinstance(time, tuple) and
               all([isinstance(_, Time.Time) for _ in time]) and
               isinstance(summary, str)):
            raise ValueError

        self.time = time
        self.summary = summary
        self.timezone = time[0].time_zone

    def calendar_format(self) -> tuple[str]:
        begin, end = self.time

        return (
            begin.start.strftime(f'%Y-%m-%dT%H:%M:%S%z'),
            end.start.strftime(f'%Y-%m-%dT%H:%M:%S%z')
        )

    def submit_form(self):
        # figure out how to read in from secret JSON
        location = "800 N State College Blvd, Fullerton, CA 92831"
        begin, end = self.calendar_format()
        body = [
            ('summary', self.summary),
            ('start', {'dateTime': begin, 'timeZone': self.timezone}),
            ('end', {'dateTime': end, 'timeZone': self.timezone}),
            ('location', location)
        ]
        final_submit_body = collections.OrderedDict(body)
        return json.dumps(final_submit_body, indent=4)

    def human_readable(self) -> tuple[str]:
        """
        We are under the assumption that we are using this
        in conjunction with self.google_added_format
        """

        return (
            self.time[0].start.strftime("%A %B %d, %H:%M"),
            self.time[1].start.strftime("%H:%M")
        )

    def google_added_format(self) -> str:
        begin, end = self.human_readable()
        return f"from {begin} to {end}"

"""Module containing the EventPacket"""

import dataclasses
import datetime
import typing
import collections
import os
import pytz


@dataclasses.dataclass
class EventPacket:
    """Represents an object to be sent to a calendar API"""

    start: datetime.datetime
    end: datetime.datetime
    summary: str = "Jared's Work"

    def duration(self):
        """How long is the event"""

        return float((self.end - self.start).seconds / 3600)

    @property
    def utc_offset(self) -> typing.List[str]:
        """Get the utc offset for both times"""

        return list(
            map(
                lambda x: pytz.timezone(os.environ["TIMEZONE"])
                .localize(x)
                .strftime("%z"),
                (self.start, self.end),
            )
        )

    def form_submit_body(self):
        """Dictionary representation for the current event to be passed to the API"""

        start, end = map(
            lambda x, y: x.strftime(f"%Y-%m-%dT%H:%M:%S{y}"),
            (self.start, self.end),
            self.utc_offset,
        )
        body = [
            ("summary", self.summary),
            (
                "start",
                {"dateTime": start, "timeZone": os.environ["TIMEZONE"]},
            ),
            (
                "end",
                {"dateTime": end, "timeZone": os.environ["TIMEZONE"]},
            ),
            ("location", os.environ["STAR_LOCATION"]),
        ]

        return collections.OrderedDict(body)

    def __add__(self, rhs) -> float:
        """To be used with sum"""

        return self.duration() + rhs.duration()

    def __repr__(self) -> str:
        return f"from {self.start.strftime('%A %B %d %H:%M')} to {self.end.strftime('%H:%M')}"

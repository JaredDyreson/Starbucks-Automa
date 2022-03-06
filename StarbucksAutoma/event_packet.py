"""Module containing the EventPacket"""

import dataclasses
import datetime
import json
import typing
import collections

from StarbucksAutoma.constants import TIMEZONE, LOCATION, UTC_OFFSET


@dataclasses.dataclass
class EventPacket:
    """Represents an object to be sent to a calendar API"""

    start: datetime.datetime
    end: datetime.datetime
    summary: str = "Jared's Work"

    def duration(self):
        """How long is the event"""

        return float((self.end - self.start).seconds / 3600)

    def form_submit_body(self) -> typing.Dict:
        """Dictionary representation for the current event to be passed to the API"""

        start, end = map(
            lambda x: x.strftime(f"%Y-%m-%dT%H:%M:%S{UTC_OFFSET}"),
            (self.start, self.end),
        )

        return {
            "summary": {
                "start": {"dateTime": start, "timeZone": TIMEZONE},
                "end": {"dateTime": end, "timeZone": TIMEZONE},
                "location": LOCATION,
            }
        }

    def __add__(self, rhs) -> float:
        """To be used with sum"""

        return self.duration() + rhs.duration()

    def __repr__(self) -> str:
        return f"from {self.start.strftime('%A %B %d %H:%M')} to {self.end.strftime('%H:%M')}"

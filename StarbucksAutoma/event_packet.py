"""Module containing the EventPacket"""

import dataclasses
import datetime

@dataclasses.dataclass
class EventPacket:
    """Represents an object to be sent to a calendar API"""

    start: datetime.datetime
    end: datetime.datetime
    summary: str = "Jared's Work"

    def duration(self):
        """How long is the event"""

        return float((self.end -self.start).seconds / 3600)

    def __add__(self, rhs) -> float:
        return self.duration() + rhs.duration()

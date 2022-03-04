"""A class representing a work week"""

import dataclasses
import functools
import math
import operator
import typing

from StarbucksAutoma.event_handler import GoogleEventHandler
from StarbucksAutoma.event_packet import EventPacket
from StarbucksAutoma.constants import PAY_RATE


from termcolor import colored

def truncate(x: int, n: int) -> float:
    """Remove the leading decimal places"""

    return math.trunc((10 ** n) * x) / (10 ** n)


@dataclasses.dataclass
class WorkWeek:
    days_working: typing.List[EventPacket]
    current_week_string_: str

    @property
    def duration(self) -> float:
        """How many hours will the individual be at work"""

        return functools.reduce(operator.add, self.days_working)

    @property
    def payable_hours(self) -> float:
        """How many hours will the individual be paid for"""

        return sum(
            i.duration() if i.duration() < 5 else i.duration() - 0.5
            for i in self.days_working
        )

    @property
    def projected_income(self) -> float:
        """Calculate the individual's income before taxes"""

        return truncate(self.payable_hours * PAY_RATE, 2)

    def add_to_calendar(self):
        """Add each individual event to a calendar API"""

        for _ in self.days_working:
            pass

    def __repr__(self):
        messages: typing.Tuple[str, str, str] = (
            f"[+] Adding all events for the week of {self.current_week_string_}",
            f"[+] Scheduled hours: {self.duration}",
            f"[+] Projected pay: ${self.projected_income}",
        )
        return "\n".join(
            map(lambda x, y: colored(x, y), messages, ("blue", "magenta", "green"))
        )

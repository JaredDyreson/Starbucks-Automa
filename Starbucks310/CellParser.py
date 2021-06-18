#!/usr/bin/env python3.10

import datetime
import re
import textwrap

import Time


class Cell:
    def __init__(self, message: str):
        if not(isinstance(message, str)):
            raise ValueError(
                f'expected `str`, received {type(message).__name__}')
        self.message = message
        self._expression = """
        (?P<begin>\d{2}\:\d{2})\s*(?P<btod>[a|p]m)\s*\-\s*(?P<end>\d{2}\:\d{2})\s*(?P<etod>[a|p]m)
        ?(?P<type>.*)
        (?P<time>\d+\.\d{2})\s*hr?s
        """
        self._re = re.compile(textwrap.dedent(self._expression).strip())
        self.match = self._re.match(self.message)

    def create_tuple(self, seeded_date: datetime.datetime) -> tuple[Time.Time]:
        if not(self.match):
            raise Exception('parsing error')
        match self.match.groups():
            case[begin, btod, end, etod, _, _]:
                return (Time.Time(f'{begin} {btod}', "America/Los_Angeles", seeded_date), Time.Time(f'{end} {etod}', "America/Los_Angeles", seeded_date))
            case _:
                raise Exception('parsing error')

    def create_json(self) -> dict:

        match(container := self.match.groups()):
            case[begin, _, end, _, _type, duration]:
                return {
                    "begin": begin,
                    "end": end,
                    "type": _type,
                    "duration": duration
                }
            case _:
                raise Exception(
                    f'expected the following format: [begin, end, _type, duration], received: {container}')

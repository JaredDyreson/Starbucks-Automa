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

        if not(self.match):
            raise Exception('parsing error!')

        match(container := self.match.groups()):
            case[_, _, _, _, _, _]:
                self.container = container
                pass
            case _:
                raise Exception(
                    f'parsing error in self.message text: {self.message}')

    def create_tuple(self, seeded_date: datetime.datetime) -> tuple[Time.Time]:
        begin, btod, end, etod, _, _ = self.container
        return (Time.Time(f'{begin} {btod}', "America/Los_Angeles", seeded_date),
                Time.Time(f'{end} {etod}', "America/Los_Angeles", seeded_date))

    def create_json(self) -> dict:
        begin, _, end, _, _type, duration = self.container

        return {
            "begin": begin,
            "end": end,
            "type": _type,
            "duration": duration
        }

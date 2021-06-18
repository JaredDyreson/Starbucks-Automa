#!/usr/bin/env python3.10

import datetime
import re
import textwrap


class Time:
    def __init__(self, begin: str):
        if not(isinstance(begin, str)):
            raise ValueError(f'expected `(str, str)`')
        self.start = self.create_time_object(begin)

    def create_time_object(self, string_repr: str) -> datetime.datetime:
        """
        Convert string to datetime object
        Following example is allowed: 11:00 am
        Following example not allowed: 11|00 pm
        """

        if not(isinstance(string_repr, str)):
            raise ValueError(
                f'expected `str`, received {type(string_repr).__name__}')
        return datetime.datetime.strptime(string_repr, '%I:%M %p')

    def append_daypart(self, string: str) -> datetime.datetime:
        """
        create_time_object will not take into account which day of
        the week it is apart of
        This method seeks to append a date to the current datetime object
        associated with this class instance
        """

        start_date = datetime.datetime.strptime(string, '%m/%d/%Y')
        return datetime.datetime.combine(
            start_date,
            self.start
        )


class Cell:
    def __init__(self, message: str):
        if not(isinstance(message, str)):
            raise ValueError(
                f'expected `str`, received {type(message).__name__}')
        self.message = textwrap.dedent(message)
        self._expression = """
        (?P<begin>\d{2}\:\d{2})\s*(?P<btod>[a|p]m)\s*\-\s*(?P<end>\d{2}\:\d{2})\s*(?P<etod>[a|p]m)
        ?(?P<type>.*Coverage)
        (?P<time>\d+\.\d{2})\s*hr?s
        """
        self._re = re.compile(textwrap.dedent(self._expression))
        self.match = self._re.match(self.message)

    def create_tuple(self) -> tuple[Time]:
        if not(self.match):
            raise Exception('parsing error')
        match self.match.groups():
            case[begin, btod, end, etod, _, _]:
                return (Time(f'{begin} {btod}'), Time(f'{end} {etod}'))
            case _:
                raise Exception('parsing error')

    def create_json(self) -> dict:

        match(container := self.create_tuple()):
            case[begin, end, _type, duration]:
                return {
                    "begin": begin,
                    "end": end,
                    "type": _type,
                    "duration": duration
                }
            case _:
                raise Exception(
                    f'expected the following format: [begin, end, _type, duration], received: {container}')


C = Cell("""
        11:00 am - 03:30 pm
        Coverage
        4.50 hrs
        """
         )
begin, end = C.create_tuple()

print(begin, end)

import datetime

import sys
sys.path.insert(1, '/usr/lib/python3.9/site-packages')


class Time:
    def __init__(self, begin: str, time_zone: str, seeded_date=None):
        if not(isinstance(begin, str)):
            raise ValueError(f'expected `(str, str)`')
        self.start = self.create_time_object(begin)
        self.time_zone = time_zone
        if(seeded_date):
            self.append_daypart(seeded_date)

    def create_time_object(self, string_repr: str) -> datetime.datetime:
        """
        Convert string to datetime object
        Following example is allowed: 11:00 am
        Following example not allowed: 11|00 pm
        """

        if not(isinstance(string_repr, str)):
            raise ValueError(
                f'expected `str`, received {type(string_repr).__name__}')
        return datetime.datetime.strptime(string_repr, '%I:%M %p').time()

    def append_daypart(self, day: datetime.datetime):
        """
        create_time_object will not take into account which day of
        the week it is apart of
        This method seeks to append a date to the current datetime object
        associated with this class instance
        """

        if not(isinstance(day, datetime.datetime)):
            raise ValueError(
                f'expected `datetime.datetime`, received: {type(day).__name__}')

        default_time = datetime.datetime.combine(
            day,
            self.start,
        )

        import pytz
        self.start = default_time.astimezone(pytz.timezone(self.time_zone))

    def is_rollover(self, other) -> bool:
        """
        Checks if the current shift extends into the next day
        The other day must be in the past relative to the current day

        Example: start == 15:30 (06/20)
                 end == 03:30 (06/20)
        We would then increment end.datetime one day in the future
        This method only works for one day in the future and does not account
        for 48/72 hour increments
        """

        return other.start.time() <= self.start.time()

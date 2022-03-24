import re
import datetime


class Shift:
    def __init__(self, time):
        t1, t2 = self.components(time)

        self.start = datetime.datetime.strptime(self.fix_time(t1), "%I:%M %p")
        self.end = datetime.datetime.strptime(self.fix_time(t2), "%I:%M %p")

        # valid_time = re.compile("(\d*?)\:(\d{1})")
        # s_valid, e_valid = valid_time.match(start), valid_time.match(end)
        # print(start, end)
        # self.role = role

    def fix_time(self, tup: tuple):
        """
        This is really messy and I don't like it
        """

        s, state = tup
        valid_time = re.compile("(^0)")
        try:
            _ = int(s)
            s = f"0{s}:00 {state}"
        except ValueError:
            val = s.split(":")[0]
            sub = f"0{val}"
            s = f"{sub if int(val) < 10 else val}:00 {state}"
        return s

    def components(self, time: str) -> tuple:
        """
        Returns the following structure:
        (start, AM|PM, end, AM|PM)
        """

        splitted = time.split()
        time_scheduled, role = "".join(splitted[:1]), " ".join(splitted[1:])
        time_split = re.compile(
            "((?P<start>\d*\:?\d*)?(?P<sstate>(AM|PM)))\-((?P<end>\d*\:?\d*)?(?P<estate>(AM|PM)))"
        ).match(time_scheduled)
        return (
            (time_split.group("start"), time_split.group("sstate")),
            (time_split.group("end"), time_split.group("estate")),
        )

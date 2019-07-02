#!/usr/bin/env python3.5

# NOTES
# Operator Overloading --> https://www.geeksforgeeks.org/operator-overloading-in-python/

from datetime import datetime


class time_struct():
        def __init__(self):
                self.begin = self.end = self.summary = None
        def __eq__(self, other):
                if(self.begin == other.begin) and (self.end == other.end) and (self.summary == other.summary):
                        return True
                return False
        def __ne__(self, other):
                return not self.__eq__(self, other)
        def gen_human_readable(self, time_obj):
                return datetime.strptime(time_obj, "%Y-%m-%d{}%H:%M:%S".format("T")).strftime("%A %B %d, %H:%M")

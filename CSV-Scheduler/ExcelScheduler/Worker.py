import re


class Worker:
    def __init__(self, name, hours, locations):
        self.reg = re.compile("(?P<lname>\w+)\,\s(?P<fname>\w+)").match(name)
        self.fname, self.lname = self.reg.group("fname"), self.reg.group("lname")
        self.hours = hours
        self.locations = locations

    def __repr__(self):
        return f"{self.fname} {self.lname} {self.locations}"

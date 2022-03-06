#!/usr/bin/env python3.8

import csv
import re
import datetime
from ExcelScheduler.Shift import Shift
from ExcelScheduler.Worker import Worker
import os


def get_days(starting: datetime.datetime):
    return [starting+datetime.timedelta(days=x) for x in range(0, 7)]

def slice_stream(contents: list):
    return [contents[x:x+2] for x, element in enumerate(contents) if(x % 2 == 0)]

workers = []
days_possible = []

class ExcelSheet():
    def __init__(self, source: str):
        self.source = source
        self.names = self.get_names()
        self.week = self.get_week()

    def get_names(self):
        lc = 0
        container = []

        with open(self.source) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                if(lc > 1):
                    contents = row
                    container.append(''.join(contents[:1]))
                lc+=1
            return container

    def get_week(self):
        with open(self.source) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                contents = row[0].split(" ")[1]
                return datetime.datetime.strptime(contents, "%m/%d/%Y")


def process(source_document: str, worker_name: str):
    year = None
    with open(source_document) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for x, row in enumerate(csv_reader):
            if(line_count == 0):
                """
                Get week of
                """

                matcher = re.compile("(?P<month>\d*)\/(?P<day>\d*)\/(?P<year>\d{4})")
                year = matcher.match(row[0].split(" ")[1]).group("year")
                line_count+=1
                continue
            if(line_count == 1):
                """
                Columns
                """
                current_date = f'{row[1]}/{year}'
                start = datetime.datetime.strptime(current_date, '%m/%d/%Y')
                print(start)
                days_possible = get_days(start)
            else:
                name = ''.join(row[:1])
                if(worker_name != name):
                    line_count+=1
                    continue
                unpacked = slice_stream(row[1:])
                for element in unpacked:
                    _, location = element
                    print(location)
                    s = Shift(location)
                    # workers.append(Worker(name, hours_worked, location))
            line_count+=1

Excel = ExcelSheet("inputs/Example.csv")
print(Excel.names)
print(Excel.week)
# process("inputs/Example.csv", "Canales, Alexandra")

# S = Shift("1PM-10:30PM TR MID SERVER CLOSER")

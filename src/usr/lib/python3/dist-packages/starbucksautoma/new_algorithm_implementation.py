#!/usr/bin/env python3.5

# this script will scrape the page for the current week and make a single list of start and end times  

from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import collections
import os
import getpass

from starbucksautoma import processing_rewrite
from starbucksautoma import addingEvents
from starbucksautoma import time_struct

def is_midnight(timeobj):
        return (timeobj.hour == 0) and (timeobj.minute == 0) and (timeobj.second == 0)

def scrape_page(path_to_file):

        with open(os.path.expanduser(path_to_file), 'r') as f:
                source = f.read()

        # this will allow us to search through the buffer

        soup = BeautifulSoup(source, 'html.parser')
        # find the current week

        date_string = soup.find("input", {"class": "x-form-field x-form-text"})

        # get the conent of that object

        date_range = str(date_string['value'])

        # we now split the string to put them as two separate strings

        split_time = date_range.split("-", 1)

        # set the start and end

        start = split_time[0].strip()
        end = split_time[1].strip()

        # pass all the hard work to datetime

        d1 = datetime.strptime(start, "%m/%d/%Y")
        d2 = datetime.strptime(end, "%m/%d/%Y")

        # make a waypoint so we can call these variables again

        restore_d1 = d1

        # store all of these variables so we can iterate over them

        date_array = []

        # make an array of dates from a start and end

        while(d2 >= d1):
                date_array.append(d1)
                 # increment the date by one
                d1 += timedelta(days=1)

        # use the waypoint
        d1 = restore_d1
        array = []
        results = soup.find_all("td", { "class": re.compile("x-grid-cell x-grid-td x-grid-cell-headerId-gridColumn[0-9]")})[:7]
        for i, element in enumerate(results):
                # now this is where we find each cell that a possible time work can occur
                condition = element.find("div", {"class": "Job-time-ellipsis"})
                # this is how we are exporting our data
                s = time_struct.time_struct()
                if condition is not None:
                        r_time = datetime.strptime(str(condition.text).split("-", 1)[0].strip(), "%I:%M %p")
                        r_time_two = datetime.strptime(str(condition.text).split("-", 1)[1].strip(), "%I:%M %p")
                        s.start_time = date_array[i].replace(hour=r_time.hour, minute=r_time.minute, second=r_time.second)
                        s.end_time = date_array[i].replace(hour=r_time_two.hour, minute=r_time_two.minute, second=r_time_two.second)
                        # the only edge case that I can think of at the moment is if the end time is midnight, we need to add exactly one day to the end_time because it is not the same day we started
                        if is_midnight(s.end_time):
                                s.end_time+=timedelta(days=1)   
                        array.append(s)
                else:
                        array.append(None)
        total_hours = soup.find('div', {'class': 'calendar-day-totals-value'}).text.split(" ", 1)[0]
        current_week = str(soup.find_all('input', {'role': 'textbox'})[0]['value'])
        return array, current_week, total_hours 

def addweekrefactored(struct_list, currentweek):
        google_calendar_bot = addingEvents.GoogleEventHandler()
        for element in struct_list:
                if element is not None:
                     event = processing_rewrite.formSubmittableJSON(element.start_time, element.end_time)
                     google_calendar_bot.add_event(event)
def write_to_file(struct_list, current_week, archive="/home/{}/Applications/starbucks_automa/work_schedules/".format(getpass.getuser())):
       for element in struct_list:
               if element is not None:
                       content="{}\n".format(str(processing_rewrite.formSubmittableJSON(element.start_time, element.end_time)))
       start = datetime.strptime(current_week.split("-", 1)[0].strip(), "%m/%d/%Y").strftime("%B %d")
       end =  datetime.strptime(current_week.split("-", 1)[1].strip(), "%m/%d/%Y").strftime("%B %d")
       current_week = "Week of {} - {}".format(start, end)
       if os.path.isfile("{}/{}.json".format(archive, current_week)):
               print("[-] {} is already logged".format(current_week))
       else:
               with open("{}/{}.json".format(archive, current_week),"w") as f:
                       f.write(content)
def remove_week(struct_list, currentweek):
        google_calendar_bot = addingEvents.GoogleEventHandler()
        print("[+] Removing week: {}".format(currentweek))
        for element in struct_list:
                if element is not None:
                     event = processing_rewrite.formSubmittableJSON(element.start_time, element.end_time)
                     if not flag:
                             print(event_id)

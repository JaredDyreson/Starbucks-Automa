#!/usr/bin/env python3.8


import math
from termcolor import colored

from StarbucksAutoma import event_handler


def truncate(x, n):
    return math.trunc((10**n)*x)/(10**n)


class starbucks_week():
    def __init__(self, current_week: list, current_week_str: str):
        self.current_week_ = current_week
        self.current_week_string_ = current_week_str

    def __repr__(self):
        event_message_ = "[+] Adding all events for week of {}...".format(self.current_week_string_)
        scheduled_hours_message_ = "[+] Scheduled hours: {}".format(self.get_hours_scheduled())
        projected_pay_message_ = "[+] Projected pay: ${}".format(self.get_projected_income())
        return "{}\n{}\n{}".format(
            colored(event_message_, 'blue'),
            colored(scheduled_hours_message_, 'magenta'),
            colored(projected_pay_message_, 'green')
        )

    def get_hours_scheduled(self):
        """
        Add up all the hourst for a given week (including lunches)
        """

        return sum([element.get_time_elapsed() for element in self.current_week_])

    def get_hours_for_overall_pay(self):
        """
        Add up all the hours for a given week (not including lunches)
        Can be used to calculate gross pay
        """

        total = 0
        for day in self.current_week_:
            hours_worked_ = day.get_time_elapsed()
            if(hours_worked_ >= 5):
                total += ((hours_worked_-0.5))
            else:
                total += (hours_worked_)
        return total

    def get_projected_income(self):
        """
        Calculate total pay for a given week
        """

        PAY_RATE = 15.02
        calculated_ = self.get_hours_for_overall_pay()*PAY_RATE
        return truncate(calculated_, 2)

    def add_to_calendar(self):
        """
        Add each individual event using the Google Calendar API
        """
        google_calendar_bot = event_handler.GoogleEventHandler()
        for event in self.current_week_:
            google_calendar_bot.add_events(event)

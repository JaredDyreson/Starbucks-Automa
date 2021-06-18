#!/usr/bin/env python3.10

# FireFox webdriver helper functions

from __future__ import print_function

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException

import datetime
import getpass
import json
import os
import pathlib
import re
import time


class PortalDriver():
    def __init__(self, driver):
        self.driver = driver

    def get_current_week(self) -> str:
        return "06/14/2021 - 06/20/2021"

    # def filter_stitch(self):
        # """
        # Create a list of event_packet objects that will be submitted
        # to Google Calendar via an API request
        # """

        # filtered = []
        # self.load_inner_html_page()
        # current_week = self.get_projected_week()
        # scraped_week = self.scrape_current_week()

        # for x, day in enumerate(scraped_week):
        # if not(day):
        # continue

        # cell = Cell(day)

    def get_projected_week(self) -> list[datetime.datetime]:
        """
        Given a week string range, create a list of datetime objects.
        These will be combined in the starbucks_week.stitch()
        function call
        """

        container: list[datetime.datetime] = []
        _re = re.compile(
            "(?P<begin>\d{2}\/\d{2}\/\d{4})\s*\s\-\s*(?P<end>\d{2}\/\d{2}\/\d{4})")
        _match = _re.match((week := self.get_current_week()))
        if not(_match):
            raise Exception(f'regex did not match, received: {week}')
        match _match.groups():
            case[alpha, omega]:
                alpha, omega = datetime.datetime.strptime(
                    alpha, "%m/%d/%Y"), datetime.datetime.strptime(omega, "%m/%d/%Y")
                while(omega >= alpha):
                    container.append(alpha)
                    alpha += datetime.timedelta(days=1)
            case _:
                raise Exception(f'parsing error, received {week}')
        return container


_ = PortalDriver(None)
container = _.get_projected_week()
print(container)
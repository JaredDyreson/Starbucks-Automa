#!/usr/bin/env python3.8

# Firefox webdriver helper functions

from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import os
from datetime import datetime, timedelta, time
import getpass

from StarbucksAutoma import event_packet as ts
from StarbucksAutoma import db_handler as db
from StarbucksAutoma.json_parser import jsonparser
import pathlib
import re
import json


username_ = getpass.getuser()
portal_url = "https://starbucks-wfmr.jdadelivers.com/retail"
print('hey look mom! no hands!')

jp = jsonparser()

"""
NOTE:

These would be nice to have implemented

- Regex to get current hours done: "Punched Hours\n(?P<coverage>\d+\.\d+)"

"""


class portal_driver():
    def __init__(self, driver: webdriver, jparser=jp):
        self.driver = driver
        self.jp = jparser

    def filter_stitch(self):
        """
        Create a list of event_packet objects that will be submitted
        to Google Calendar via an API request
        """

        filtered_ = []
        is_training = False
        self.load_inner_html_page()
        current_week_ = self.get_projected_week()
        time_working_regex = re.compile(
            "(?P<start>\d{2}\:\d{2}\s(am|pm)).*(?P<end>\d{2}\:\d{2}\s(am|pm))")
        scraped_week = self.scrape_current_week()
        c = self.get_current_week().replace('/', '_')
        c = c.replace(' ', '_')
        import pickle
        with open(f"/tmp/scratch/scraped_{c}.pkl", 'wb') as fp:
            pickle.dump(scraped_week, fp)

        for index, day in enumerate(scraped_week):
            if not(day):
                continue

            bare_week_indexed = current_week_[index]
            start, end = None, None

            if("Coverage" in day):
                """
                this still needs to be tested
                """

                if("Training" in day):
                    base = day.split()
                    start = "{} {}".format(base[0], base[1])
                    end = "{} {}".format(base[9], base[10])
                    is_training = True

                elif("NonCoverage" in day):
                    """
                    This still needs to be tested further
                    """

                    start = day.split("Coverage")[
                        0].strip().split("-")[0].strip()
                    print(day.split("Coverage"))
                    end = day.split("NonCoverage")[1].strip().split(
                        "-")[1].strip().split()
                    print(day.split("NonCoverage"))
                    end = ' '.join(end[:2])
                else:
                    match = time_working_regex.match(day)
                    if(match):
                        start, end = match.group("start"), match.group("end")

                start = datetime.strptime(start, "%I:%M %p").time()
                end = datetime.strptime(end, "%I:%M %p").time()

                combined_datetime_start_ = datetime.combine(
                    bare_week_indexed, start)
                combined_datetime_end_ = datetime.combine(
                    bare_week_indexed, end)
                if(time() == combined_datetime_end_.time()):
                    combined_datetime_end_ += timedelta(days=1)
                event = ts.event_packet(
                    combined_datetime_start_, combined_datetime_end_)
                if(is_training):
                    event.summary = "Jared's Work (Training Included)"
                filtered_.append(event)

            if("Time Off" in day):
                string_version = datetime.strftime(
                    bare_week_indexed, "%Y-%m-%d %H:%M:%S")
                human_readable = datetime.strptime(
                    string_version, "%Y-%m-%d %H:%M:%S").strftime("%A %B %d")
                print(f"[+] Scheduled time off for {human_readable}")

        return filtered_

    def get_projected_week(self):
        """
        Given a week string range, create a list of datetime objects.
        These will be combined in the starbucks_week.stitch()
        function call
        Returns: list of datetime objects
        """

        date_range = []
        sleep(3)
        split_week = self.get_current_week().split("-", 1)

        s = split_week[0].strip()
        e = split_week[1].strip()

        alpha = datetime.strptime(s, "%m/%d/%Y")
        omega = datetime.strptime(e, "%m/%d/%Y")
        while(omega >= alpha):
            date_range.append(alpha)
            alpha += timedelta(days=1)
        return date_range

    def scrape_current_week(self):
        """
        Get a list of web driver elements that contain days working
        """

        self.load_inner_html_page()
        return [element.text for element in self.driver.find_elements_by_xpath(
            '//*[contains(@class,"x-grid-cell x-grid-td x-grid-cell-headerId-gridColumn")]')[:7]]

    def load_inner_html_page(self):
        """
        Load the sub page of the portal that will allow access to the schedule
        """

        try:
            sub_html_link = self.driver.find_element_by_css_selector(
                "iframe[class='x-component x-fit-item x-component-default']").get_attribute('src')
            self.driver.get(sub_html_link)
            sleep(8)
        except NoSuchElementException:
            pass

    def find_partner_password_field(self):
        """
        Find and fille the final password field for login
        Returns clickable submit button on the page
        """

        password_field = self.driver.find_element_by_css_selector(
            "input[type='password']")
        password_field.send_keys(self.jp.getjsonkey("password"))
        return self.driver.find_element_by_css_selector("input[type='submit']")

    def fill_and_submit_password_field(self):
        self.find_partner_password_field().click()

    def find_partner_username(self):
        """
        Find and fille the username field  for login
        Retuns a clickable submit button on the page
        """

        try:
            username_field = self.driver.find_element_by_css_selector(
                "input[class='textbox txtUserid']")
        except NoSuchElementException:
            sleep(4)
            username_field = self.driver.find_element_by_css_selector(
                "input[class='textbox txtUserid']")
        username_field.send_keys(self.jp.getjsonkey("username"))
        return self.driver.find_element_by_css_selector("input[type='submit']")

    def fill_and_submit_username_field(self):
        self.find_partner_username().click()

    def find_two_factor_auth(self):
        """
        Find and fill the two factor authentication portion for login
        Returns clickable submit button on the page
        """

        security_question = self.driver.find_element_by_css_selector(
            "span[class='bodytext lblKBQ lblKBQ1']")
        security_question_field = self.driver.find_element_by_css_selector(
            "input[class='textbox tbxKBA tbxKBA1']")
        security_button = self.driver.find_element_by_css_selector(
            "input[type='submit']")

        if(security_question.text == self.jp.getjsonkey("sec_question_one")):
            security_question_field.send_keys(
                self.jp.getjsonkey("sec_one_answer"))
        else:
            security_question_field.send_keys(
                self.jp.getjsonkey("sec_two_answer"))
        return security_button

    def go_to_landing_page(self):
        print("[+] Loading portal login page....")
        self.driver.get(portal_url)

        print("[+] Finding and filling username field....")
        self.wait_for_element("span[class='sbuxheadertext']")
        self.fill_and_submit_username_field()

        print("[+] Finding and filling in two factor authentication...")
        self.wait_for_element(
            "span[class='bodytext lblKBQIndicator lblKBQIndicator1']")
        self.fill_and_submit_two_factor_auth()

        print("[+] Finding and filling in password field...")
        self.wait_for_element("a[id='sbuxForgotPasswordURL']")
        self.fill_and_submit_password_field()
        self.wait_for_element(
            "img[class='x-img rp-redprairie-logo x-img-default']")

    def go_to_next_week(self):
        self.driver.find_element_by_css_selector(
            "span[id='button-1029-btnIconEl']").click()

    def fill_and_submit_two_factor_auth(self):
        self.find_two_factor_auth().click()

    def wait_for_element(self, selector: str, delay=40):
        WebDriverWait(self.driver, delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def kill_marionette(self):
        self.driver.quit()
        os.remove("geckodriver.log")

    def get_current_week(self):
        return self.driver.find_element_by_css_selector(
            "input[id='textfield-1026-inputEl']").get_attribute("value")

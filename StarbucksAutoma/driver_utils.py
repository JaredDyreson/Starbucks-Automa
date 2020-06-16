#!/usr/bin/env python3.8

# Firefox webdriver helper functions

from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time
import os
from collections import OrderedDict
from datetime import datetime, timedelta
import getpass
import re

from StarbucksAutoma import json_parser as jp
from StarbucksAutoma import time_struct as ts
from StarbucksAutoma import db_handler as db

username_ = getpass.getuser()
portal_url = "https://starbucks-wfmr.jdadelivers.com/retail"
lite = db.lite_handler("credentials", "/home/{}/Applications/starbucks_automa/credentials/config.db".format(username_))

class portal_driver():
  def __init__(self, driver: webdriver, db_handler=lite):
    self.driver = driver
    self.lite_handler = db_handler
  def filter_stitch(self):
    # return one list of time_struct objects that will submitted to the Google Calendar
    filtered_ = []
    is_training = False
    self.load_inner_html_page()
    current_week_ = self.get_projected_week()
    for index, day in enumerate(self.scrape_current_week()):
      # print("content of day.text: {}".format(day.text))
      if("Coverage" in day.text):
        if("Training" in day.text):
          base = day.text.split()
          start = "{} {}".format(base[0], base[1])
          end = "{} {}".format(base[9], base[10])
          is_training = True
        elif("NonCoverage" in day.text):
          start = day.text.split("Coverage")[0].strip().split("-")[0].strip()
          end = day.text.split("NonCoverage")[1].strip().split("-")[1].strip().split()
          end = ' '.join(end[:2])
        else: 
          start = day.text.split("Coverage")[0].strip().split("-")[0].strip()
          end = day.text.split("Coverage")[0].strip().split("-")[1].strip()

        
        start = datetime.strptime(start, "%I:%M %p").time()
        end = datetime.strptime(end, "%I:%M %p").time()

        bare_week_indexed = current_week_[index]

        combined_datetime_start_ = datetime.combine(bare_week_indexed, start)
        combined_datetime_end_ = datetime.combine(bare_week_indexed, end)
        if(datetime.today().time().replace(hour=0, minute=0, second=0, microsecond=0) == combined_datetime_end_.time()):
          combined_datetime_end_+=timedelta(days=1)
        event = ts.time_struct(combined_datetime_start_, combined_datetime_end_)
        if(is_training): event.summary = "Jared's Work (Training Included)"
        filtered_.append(event)
    return filtered_
  def get_projected_week(self):
    # given a week string range, create a list of datetime.date objects that will be combined in starbucks_week.stitch()
    # return : list => datetime.dateime objects

    date_range = []
    time.sleep(3)
    split_week = self.get_current_week().split("-", 1)

    s = split_week[0].strip()
    e = split_week[1].strip()

    alpha = datetime.strptime(s, "%m/%d/%Y")
    omega = datetime.strptime(e, "%m/%d/%Y") 
    while(omega >= alpha):
      date_range.append(alpha)
      alpha+=timedelta(days=1)
    return date_range
  def scrape_current_week(self):
    # return: list of driver web elements that contain days working
    self.load_inner_html_page()
    return self.driver.find_elements_by_xpath('//*[contains(@class,"x-grid-cell x-grid-td x-grid-cell-headerId-gridColumn")]')[:7]
  def load_inner_html_page(self):
  # load the sub page of portal that will allow us access to the schedule itself
    try:
      sub_html_link = self.driver.find_element_by_css_selector("iframe[class='x-component x-fit-item x-component-default']").get_attribute('src')
      self.driver.get(sub_html_link)
      # hardcoded time to wait is better in this case because either a loading animation can occur or a page error can be present
      time.sleep(8)
    except NoSuchElementException:
      pass  
  def find_partner_password_field(self):
    # find and fill the final password field for login
    # return: selenium web element which is the submit button
    password_field = self.driver.find_element_by_css_selector("input[type='password']")
    password_field.send_keys(self.lite_handler.get_value("password"))
    return self.driver.find_element_by_css_selector("input[type='submit']")

  def fill_and_submit_password_field(self):
    self.find_partner_password_field().click()

  def find_partner_username(self):
    # find and fill the username field for login
    # return: selenium web element which is the submit button
    try:
      username_field = self.driver.find_element_by_css_selector("input[class='textbox txtUserid']")
    except NoSuchElementException:
      time.sleep(4)
      username_field = self.driver.find_element_by_css_selector("input[class='textbox txtUserid']")
    username_field.send_keys(self.lite_handler.get_value("username"))
    return self.driver.find_element_by_css_selector("input[type='submit']")
  def fill_and_submit_username_field(self):
    self.find_partner_username().click()

  def find_two_factor_auth(self):
    # find and fill the two factor authentication portion for login
    # return: selenium web element which is the submit button
    security_question = self.driver.find_element_by_css_selector("span[class='bodytext lblKBQ lblKBQ1']")
    security_question_field = self.driver.find_element_by_css_selector("input[class='textbox tbxKBA tbxKBA1']")
    security_button = self.driver.find_element_by_css_selector("input[type='submit']")
    if(security_question.text == self.lite_handler.get_value("sec_question_one")):
      security_question_field.send_keys(self.lite_handler.get_value("sec_answer_one"))
    else:
      security_question_field.send_keys(self.lite_handler.get_value("sec_answer_two"))
    return security_button
  def go_to_landing_page(self):
    print("[+] Loading portal login page....")
    self.driver.get(portal_url)

    print("[+] Finding and filling username field....")
    self.wait_for_element("span[class='sbuxheadertext']")
    self.fill_and_submit_username_field()

    print("[+] Finding and filling in two factor authentication...")
    self.wait_for_element("span[class='bodytext lblKBQIndicator lblKBQIndicator1']")
    self.fill_and_submit_two_factor_auth()

    print("[+] Finding and filling in password field...")
    self.wait_for_element("a[id='sbuxForgotPasswordURL']")
    self.fill_and_submit_password_field()
    self.wait_for_element("img[class='x-img rp-redprairie-logo x-img-default']")
  def go_to_next_week(self):
    self.driver.find_element_by_css_selector("span[id='button-1029-btnIconEl']").click()
  def fill_and_submit_two_factor_auth(self):
    self.find_two_factor_auth().click()
  def wait_for_element(self, element_css_selector: str, delay=20):
    WebDriverWait(self.driver, delay).until(ec.presence_of_element_located((By.CSS_SELECTOR, element_css_selector)))
  def kill_marionette(self):
    self.driver.quit()
    os.remove("geckodriver.log")
  def get_current_week(self):
    return self.driver.find_element_by_css_selector("input[id='textfield-1026-inputEl']").get_attribute("value")

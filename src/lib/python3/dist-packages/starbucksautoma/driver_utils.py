#!/usr/bin/env python3.5

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
from datetime import datetime

from starbucksautoma import json_parser as jp
from starbucksautoma import time_struct as ts

class portal_driver():
	def __init__(self, driver: webdriver, jparser: jp.jsonparser):
		self.driver = driver
		self.parser = jparser
	def scrape_week_merge_to_dict(self, from_page: list):
		# accepts one week in the form of a list
		# adding flags for each day in week to indicate for other functions
		# ORDER MATTERS
		# returns: OrderedDict
		# key: time_struct with datetime.time objects as start and end
		# value: flag if working 

		a_dictionary = OrderedDict()
		for day in from_page:
			if("Coverage" in day.text):
				base = day.text.split('Coverage')[0].strip()
				start = base.split('-', 1)[0].strip()
				end = base.split('-', 1)[1].strip()
			
				start = datetime.strptime(start, "%I:%M %p").time()
				end = datetime.strptime(end, "%I:%M %p").time()
				a_dictionary[ts.time_struct(start, end)] = True
			else:
				a_dictionary[ts.time_struct()] = False
		return a_dictionary
	def scrape_current_week(self):
		# load the sub page of portal that will allow us access to the schedule itself
		# return: list of driver web elements that contain days working

		sub_html_link = self.driver.find_element_by_css_selector("iframe[class='x-component x-fit-item x-component-default']").get_attribute('src')
		self.driver.get(sub_html_link)
		time.sleep(8)
		# improve this ^ with this code -> https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
		# webelement: id = 'gridview-1046-record-scheduledHoursRow' and data-recordid = 'scheduledHoursRow'

		return self.driver.find_elements_by_xpath('//*[contains(@class,"x-grid-cell x-grid-td x-grid-cell-headerId-gridColumn")]')[:7]

	def find_partner_password_field(self):
		# find and fill the final password field for login
		# return: selenium web element which is the submit button
		password_field = self.driver.find_element_by_css_selector("input[type='password']")
		password_field.send_keys(self.parser.getjsonkey(key="password"))
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
		username_field.send_keys(self.parser.getjsonkey(key="username"))
		return self.driver.find_element_by_css_selector("input[type='submit']")
	def fill_and_submit_username_field(self):
		self.find_partner_username().click()

	def find_two_factor_auth(self):
		# find and fill the two factor authentication portion for login
		# return: selenium web element which is the submit button
		security_question = self.driver.find_element_by_css_selector("span[class='bodytext lblKBQ lblKBQ1']")
		security_question_field = self.driver.find_element_by_css_selector("input[class='textbox tbxKBA tbxKBA1']")
		security_button = self.driver.find_element_by_css_selector("input[type='submit']")
		if(security_question.text == "What city were you born in?"):
			security_question_field.send_keys(self.parser.getjsonkey(key="hometown"))
		elif(security_question.text == "What is your favorite hobby?"):
			security_question_field.send_keys(self.parser.getjsonkey(key="hobby"))
		return security_button
	def fill_and_submit_two_factor_auth(self):
		self.find_two_factor_auth().click()
	def wait_for_element(self, element_css_selector: str, delay=10):
		WebDriverWait(self.driver, delay).until(ec.presence_of_element_located((By.CSS_SELECTOR, element_css_selector)))
	def kill_marionette(self):
		self.driver.quit()
		os.remove("geckodriver.log")
	def get_current_week(self):
		return self.driver.find_element_by_css_selector("input[id='textfield-1026-inputEl']").get_attribute("value")

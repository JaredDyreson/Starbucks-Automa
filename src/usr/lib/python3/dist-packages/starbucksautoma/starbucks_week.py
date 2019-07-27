#!/usr/bin/env python3.5

import time
import datetime
from datetime import timedelta
from datetime import timezone
import json
from collections import OrderedDict
from starbucksautoma import adding_events as add_events
from starbucksautoma import time_struct as ts
import math

class starbucks_week():
	def __init__(self, scraped_week: OrderedDict, projected_week_str: str):
		# self.bare_week_ contains a list of empty datetime.date objects which hold the days available to work
		# these need to be merged with the time_struct object which contains the time working as both pieces of information are not given together
		self.scraped_week_ = scraped_week
		self.projected_week_string_ = projected_week_str
		self.projected_list_ = self.get_projected_week()
		self.stitched_week_ = self.stitch()

	def get_hours_scheduled(self):
		# add up all the hours for a given week
		# return: float

		return sum([element.get_time_elapsed() for element in self.stitched_week_])
	def get_projected_income(self):
		# call get_hours_scheduled and multiply by pay rate CONST
		# return: float
		PAY_RATE = 14.27
		calculated_ = self.get_hours_scheduled()*PAY_RATE
		return (math.floor(calculated_ * 100)) / 100.0
	def stitch(self):
		# combine self.bare_week_ and self.scraped_week_ into one list
		# ignore items from self.scraped_week_ that have a false attribute
		# return: list containing time_struct objects
		l = []
		for index, (time_worked, is_working) in enumerate(self.scraped_week_.items()):
			if(is_working):
				bare_week_indexed = self.projected_list_[index]

				combined_datetime_start_ = datetime.datetime.combine(bare_week_indexed, time_worked.begin)
				if(time_worked.is_midnight(time_worked.end)):
					time_worked.end+=timedelta(days=1)
				combined_datetime_end_ = datetime.datetime.combine(bare_week_indexed, time_worked.end)

				l.append(ts.time_struct(combined_datetime_start_, combined_datetime_end_))
		return l
	def add_to_calendar(self):
		# add each individual date to the Google Calendar API (from self.stitched_week)
		# return: Nothing (void)
		google_calendar_bot = add_events.GoogleEventHandler()
		for element in self.stitched_week_:
			google_calendar_bot.add_event(element)
	def get_projected_week(self):
		# given a week string range, create a list of datetime.date objects that will be combined in starbucks_week.stitch()
		date_range = []
		split_week = self.projected_week_string_.split("-", 1)

		s = split_week[0].strip()
		e = split_week[1].strip()

		alpha = datetime.datetime.strptime(s, "%m/%d/%Y")
		omega = datetime.datetime.strptime(e, "%m/%d/%Y") 
		while(omega >= alpha):
			date_range.append(alpha)
			alpha+=timedelta(days=1)
		return date_range
	def print_contents(self):
		for element in self.stitched_week_:
			print(element.form_submit_body())
def assert_test():
	from starbucksautoma import driver_utils as du
	import json_parser as jp

	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver import ActionChains
	from selenium.webdriver.firefox.options import Options
	import selenium.webdriver.support.ui as ui

	import time
	import getpass

	portal_url = "https://sbux.co/teamworks"
	headless_ = Options()
	headless_.headless = True
	driver = webdriver.Firefox(options=headless_)
	action = ActionChains(driver)
	wait = ui.WebDriverWait(driver, 60)
	p = jp.jsonparser("/home/{}/Applications/starbucks_automa/credentials/config.json".format(getpass.getuser()))

	print("[+] Loading portal login page....")
	driver.get(portal_url)
	pd = du.portal_driver(driver, p)

	print("[+] Finding and filling username field....")
	pd.wait_for_element("span[class='sbuxheadertext']")
	pd.fill_and_submit_username_field()

	print("[+] Finding and filling in two factor authentication...")
	pd.wait_for_element("span[class='bodytext lblKBQIndicator lblKBQIndicator1']")
	pd.fill_and_submit_two_factor_auth()

	print("[+] Finding and filling in password field...")
	pd.wait_for_element("a[id='sbuxForgotPasswordURL']")
	pd.fill_and_submit_password_field()
	pd.wait_for_element("img[class='x-img rp-redprairie-logo x-img-default']")
	print("[+] Scraping inner HTML page...")
	a = pd.scrape_current_week()
	print("[+] Merging current week and days working...")
	b = pd.scrape_week_merge_to_dict(a)
	week = starbucks_week(b, pd.get_current_week())
	week_of = pd.get_current_week()
	scheduled_hours = week.get_hours_scheduled()
	print("[+] Killing marionette driver...")
	pd.kill_marionette()
	print("[+] Process killed...")
	print("[+] Adding all events for week of {}...".format(week_of))
	print("[+] Scheduled hours: {}".format(scheduled_hours))
	print("[+] Projected pay: ${}".format(week.get_projected_income()))
	week.add_to_calendar()
	print("[+] Exiting....")

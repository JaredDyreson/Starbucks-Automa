#!/usr/bin/env python3.8

import time
import datetime
from datetime import timedelta, timezone

import json
from collections import OrderedDict
import math
from termcolor import colored

from starbucksautoma import adding_events as add_events
from starbucksautoma import time_struct as ts

class starbucks_week():
	def __init__(self, current_week: list, current_week_str: str):
		self.current_week_ = current_week
		self.current_week_string_ = current_week_str

	def get_hours_scheduled(self):
		# add up all the hours for a given week (including lunches)
		# return: float
		return sum([element.get_time_elapsed() for element in self.current_week_])
	def get_hours_for_overall_pay(self):
		# add up all the hours for a given week (not including lunches) and can be used to calculate total pay
		# return: float
		total = 0
		for day in self.current_week_:
			hours_worked_ = day.get_time_elapsed()
			if(hours_worked_ >= 5):
				total+=((hours_worked_-0.5))	
			else:
				total+=(hours_worked_)
		return total
	def get_projected_income(self):
		# call get_hours_scheduled and multiply by pay rate CONST
		# return: float
		PAY_RATE = 14.27
		calculated_ = self.get_hours_for_overall_pay()*PAY_RATE
		return (math.floor(calculated_ * 100)) / 100.0
		
	def add_to_calendar(self):
		# add each individual date using the Google Calendar API (from self.stitched_week)
		# return: Nothing (void)
		google_calendar_bot = add_events.GoogleEventHandler()
		for event in self.current_week_:
			google_calendar_bot.add_event(event)
	def print_contents(self):
		# print all useful information about current week 
		# return : void
		event_message_ = "[+] Adding all events for week of {}...".format(self.current_week_string_)
		scheduled_hours_message_ = "[+] Scheduled hours: {}".format(self.get_hours_scheduled())
		projected_pay_message_ = "[+] Projected pay: ${}".format(self.get_projected_income())
		print(colored(event_message_, 'blue'))
		print(colored(scheduled_hours_message_, 'magenta'))
		print(colored(projected_pay_message_, 'green'))

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

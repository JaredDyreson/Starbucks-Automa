#!/usr/bin/env python3.5

import datetime
from datetime import timedelta
from datetime import timezone
import json
import time
import collections
from starbucksautoma import json_parser as jp
import pytz
import getpass

username_ = getpass.getuser()


parser = jp.jsonparser("/home/{}/Applications/starbucks_automa/credentials/config.json".format(username_))

class time_struct(object):

	# start: datetime
	# end: datetime

	def __init__(self, start=datetime.datetime.today(), end=datetime.datetime.today(), summary="{}'s Work".format(parser.getjsonkey(key="name"))):
		self.begin = start
		self.end = end
		self.summary = summary
	@classmethod
	def from_dict(cls, body: dict):
		s = datetime.datetime.strptime(body['start'].replace("-07:00", ""), "%Y-%m-%d{}%H:%M:%S".format("T"))
		e = datetime.datetime.strptime(body['end'].replace("-07:00", ""), "%Y-%m-%d{}%H:%M:%S".format("T"))
		return cls(s, e)
	@classmethod
	def from_freebusy(cls, response: dict):
		b = str(response.get('start').get('dateTime'))
		t = str(response['end']['dateTime'])
		s = datetime.datetime.strptime(b.replace("-07:00", ""), "%Y-%m-%d{}%H:%M:%S".format("T"))
		e = datetime.datetime.strptime(t.replace("-07:00", ""), "%Y-%m-%d{}%H:%M:%S".format("T"))
		summary = response['summary']
		identification = response['id']
		return cls(s, e, summary, identification)
	def __eq__(self, other):
		return self.form_submit_body() == other.form_submit_body()

	def __ne__(self, other):
		return not self.__eq__(self, other)

	def __hash__(self):
		# dir(self): returns all of the possible attributes of this class
		# returns: hash of time_struct class
		return hash(",".join(dir(self)))

	def is_midnight(self, time_object):
		# takes in either self.begin or self.end and returns boolean
		return (time_object.hour == 0) and (time_object.minute == 0) and (time_object.second == 0)
	def google_calendar_format(self):
		# returns a list of string objects (len of 2) that can be passed to form_submit_body

		s = self.begin.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset()))
		e = self.end.strftime("%Y-%m-%d{}%H:%M:%S{}".format("T", self.get_utc_offset()))
		return [s, e]
	def get_time_elapsed(self):
		# compute total time working
		# return: float
		time_elapsed_ = (self.end - self.begin).total_seconds()
		time_elapsed_/=3600 
		return abs(time_elapsed_)
	
	def form_submit_body(self, timezone=parser.getjsonkey(key="timezone"), location=parser.getjsonkey(key="store_location")):
		body = [('summary', "{}'s Work".format(parser.getjsonkey(key="name"))),
	    ('start', {'dateTime': self.google_calendar_format()[0], 'timeZone': timezone}),
	    ('end', {'dateTime': self.google_calendar_format()[1], 'timeZone': timezone}),
	    ('location', location)]
		final_submit_body = collections.OrderedDict(body)
		return json.dumps(final_submit_body, indent=4)
	def get_utc_offset(self):
		current_offset = datetime.datetime.now(pytz.timezone(parser.getjsonkey(key="timezone"))).strftime("%z")
		return "{}:{}".format(current_offset[:3], current_offset[3:])
	def gen_human_readable(self, time_obj: datetime):
		string_version = datetime.datetime.strftime(time_obj, "%Y-%m-%d{}%H:%M:%S").format("T")
		return datetime.datetime.strptime(string_version, "%Y-%m-%d{}%H:%M:%S".format("T")).strftime("%A %B %d, %H:%M")
	def google_date_added_string(self):
		begin_h = self.gen_human_readable(self.begin)
		end_h = self.gen_human_readable(self.end)
		return "from {} to {}".format(begin_h, end_h.split()[3])
def assert_test():
	total_tests = 3
	counter = 0
	midnight_str = "00:00:00"
	c1 = datetime.datetime.now()
	c2 = (c1+timedelta(hours=4))
	c3 = datetime.datetime.strptime(midnight_str, "%H:%M:%S")
	ts1 = time_struct(c1, c2)
	ts2 = time_struct(c1, c3)
	print("ts1 [start]: {}\nts1 [end]: {}".format(ts1.begin, ts1.end))
	print("checking get_time_elapsed....")
	if(ts1.get_time_elapsed() == 4):
		print("\t[+] passed")
		counter+=1
	else:
		print("\t[-] failed")
		print("\t[-] output: {}".format(ts1.get_time_elapsed()))
	print("checking equality operator..")
	if(not ts1 == ts2):
		print("\t[+] passed")
		counter+=1
	else:
		print("\t[-] failed")
		print("ts1 hash: {}\nts2 hash: {}".format(ts1.__hash__(), ts2.__hash__()))
	print("checking google calendar format....")
	print(ts1.google_calendar_format())
	print("checking form_submit_body....")
	print(ts1.form_submit_body())
	print("checking hash function....")
	print("hash is: {}".format(ts1.__hash__()))
	if(ts2.is_midnight(ts2.end)):
		print("\t[+] passed")
		counter+=1
	else:
		print("\t[-] failed")
	print("checking human readable format....")
	print("start: {}".format(ts1.gen_human_readable(ts1.begin)))
	print("end: {}".format(ts1.gen_human_readable(ts1.end)))
	print("testing google_date_added_string function...")
	print(ts1.google_date_added_string())
	print("testing constructor from dictionary....")
	d = {
		'end': '2020-04-28T09:50:00-07:00', 
		'start': '2020-04-28T08:00:00-07:00'
	}
	test_object = time_struct.from_dict(d)
	print(test_object.form_submit_body())
	if(counter == total_tests):
		print("[+] ALL TESTS PASSED")
	else:
		print("[-] {}/{} TESTS PASSED".format(counter, total_tests))

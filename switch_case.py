#!/usr/bin/env python3.5

import os
from time import sleep

class switch_case():
	def __init__(self, dictionary_options: dict):
		self.switch_ = dictionary_options
		self.options_ = self.get_options()
	def add_function(self, name_: str, function_pointer):
		self.switch_[name_] = function_pointer
	def get_options(self):
		return list(self.switch_.keys())
	def activate_function(self, name_: str, arguments: list):
		self.switch_[name_](' '.join(arguments))
	def list_and_run_options(self, argument_list_=[]):
		while True:
			print("[+] Pick an option and pick one:")
			index_counter = 0
			for index, element in enumerate(self.get_options()):
				print("[{}] {}".format(index, element))
				index_counter = index
			print("[{}] Quit".format(index_counter+1))
			option_ = int(input("Select: "))
			if(option_ == index_counter+1):
				return
			try:
				function_run_ = self.get_options()[option_]
				self.activate_function(name_=function_run_, arguments=argument_list_)
			except IndexError:
				print("[-] Could not find proper option, cowardly refusing")
			os.system('clear')
def assert_test():
	d = {}
	s = switch_case(d)
	def test_function(argument: str):
		print(argument)
	def hello():
		print("Hello")
	s.add_function(name_="test", function_pointer=test_function)
	s.add_function(name_="hello", function_pointer=hello)
	print(s.get_options())
	s.activate_function("test", ["Hello", "World"])
	s.list_and_run_options(argument_list_=["Hello", "World"])
assert_test()

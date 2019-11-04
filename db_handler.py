#!/usr/bin/env python3.5

import sqlite3
import os

class lite_handler():
	def __init__(self, name: str, path: str):
		self.database_path = path
		self.table_name = name
		self.connection = sqlite3.connect(self.database_path)
		self.cursor = self.connection.cursor()
		initial_creation_command_ = """
		CREATE TABLE {} ( 
		username VARCHAR(10), 
		password VARCHAR(30), 
		name VARCHAR(10), 
		sec_question_one VARCHAR(100),
		sec_question_two VARCHAR(100),
		sec_answer_one VARCHAR(100),
		sec_answer_two VARCHAR(100),
		timezone VARCHAR(50),
		store_location VARCHAR(150));""".format(self.table_name)
		try:

			self.cursor.execute(initial_creation_command_)
			self.connection.commit()
		except sqlite3.OperationalError:
			pass
	def quote_elements(self, original_list: list):
		return ['"{}"'.format(element) for element in original_list]
	def add_entry(self, key_list: list, value_list: list):
		create_databse_entry_command_ = "INSERT INTO {} ({}) VALUES ({});".format(
			self.table_name,
			", ".join(self.quote_elements(key_list)),
			", ".join(self.quote_elements(value_list))
		)
		try:
			self.cursor.execute(create_databse_entry_command_)
			self.connection.commit()
		except sqlite3.OperationalError:
			pass
	def get_value(self, key: str):
		self.cursor.execute("SELECT {} FROM {}".format(key, self.table_name))
		return self.cursor.fetchone()[0]


#!/usr/bin/env python3.8
import json
import os
class jsonparser():
	def __init__(self, path=None):
		self.path = path
		if os.path.isfile(path):
			self.jsondata = self.jsondatabase(self.path)
		else:
			with open(self.path) as j:
				self.jsondata = json.load(j)
				self.keys = self.keysindata()
	def jsondatabase(self, path):
		jsonfile = open(path)
		jsonstr = jsonfile.read()
		return json.loads(jsonstr)
	def amountoftokens(self):
		return len(self.jsondata)
	def appendtojson(self, key, value, appendtoexisting=False):
		data = {}
		data[key] = value
		self.jsondata = json.dumps(data)
	def keysindata(self):
		return [key for value, key in self.jsondata.items()]
	def getjsonkey(self, key):
		return self.jsondata[key]
	def checkvalue(self, key, value):
		return(True if value == self.jsondata[key] else False)

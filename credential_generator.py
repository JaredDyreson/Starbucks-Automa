#!/usr/bin/env python3.5

from starbucksautoma import db_handler as db
# working with SQL databases -> https://github.com/microsoft/sql-server-samples/blob/master/samples/tutorials/python/pyodbc/linux/sample_python_linux.py
# more examples on SQL -> https://www.python-course.eu/sql_python.php

database_path = "config.db"

keys = ["username", "password", "name", "sec_question_one", "sec_question_two", "sec_answer_one", "sec_answer_two", "timezone", "store_location"]

values = ["US2404222", "u0MsIs1$^L$8Rw", "Jared",  "What city were you born in?", "What is your favorite hobby?", "Fullerton", "Coding", "America/Los_Angeles", "15010 Imperial Hwy, La Mirada, CA 90638"]


print("[+] Creating the table credentials....")
handler = db.lite_handler("credentials", database_path)
print("[+] Created...")

print("[+] Adding in current credentials")
handler.add_entry(keys, values)

# we can fetch a certain variable based on column name
"""
data used to look like this:
{
	"key": "value"
}

where now it looks like this
+-----+
|key  |
+-----+
|value|
+-----+
"""

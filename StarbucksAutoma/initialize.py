#!/usr/bin/env python3.8

import os
from getpass import getpass
from exceptions import *
import json

"""
This portion must be run as root to ensure that file permissions are properly set
We run as root, then change permissions to 600, which is read and write by owner
We are also assuming that the user is running either Linux or MacOS.
Timezone support is not included for Windows, please consult
the list of timezones dumped from timedatectl on the StarbucksAutoma wiki
"""


class initalizer():
    def __init__(self):
        self.configuration_dir = "/etc/StarbucksAutoma"
        self.sub_dirs = ["configuration",
                        "credentials",
                        "release_builds",
                        "work_schedules"]
        self.ensure_nix()
        self.ensure_root()

    def ensure_root(self):
        if(os.getuid() != 0):
            raise EnviornmentException("Run as root")

    def ensure_nix(self):
        if(os.name == "nt"):
            raise EnviornmentException("Windows not supported")

    def make_conf_structure(self) -> None:
        if(not os.path.exists(self.configuration_dir)):
            os.mkdir(self.configuration_dir)
        for path in self.sub_dirs:
            os.mkdir(os.path.join(self.configuration_dir, path))

    def make_user_config(self) -> None:
        username = input("Starbucks Username: ")
        password = getpass()
        name = input("Your first name: ")
        sec_one = getpass("2FA Question 1 Answer: ")
        sec_two = getpass("2FA Question 2 Answer: ")
        tz = os.popen("timedatectl status | awk '/Time zone/ {print $3}'").read().strip()
        location = input("Store location: ")

        print(username, password, sec_one, sec_two, tz)

        payload = {
            "username": username,
            "password": password,
            "name": name,
            "sec_one_answer": sec_one,
            "sec_two_answer": sec_two,
            "timezone": tz,
            "store_location": location
        }
        with open("{}/credentials/config.json".format(self.configuration_dir), "w") as fp:
            json.dump(payload, fp)
        os.system("chmod 600 {}/credentials/config.json".format(self.configuration_dir))


init = initalizer()
init.make_user_config()

#!/usr/bin/env python3.8

import os
from getpass import getpass
from exceptions import *
import json
import subprocess
from sudo_execute.sudo_execute import sudo_execute
import json_parser

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

    def currently_logged_in(self) -> list:
        return [user for user in subprocess.check_output(["users"], encoding="utf-8").split('\n') if user]

    def make_conf_structure(self) -> None:
        if(not os.path.exists(self.configuration_dir)):
            os.mkdir(self.configuration_dir)
        for path in self.sub_dirs:
            os.mkdir(os.path.join(self.configuration_dir, path))

    def chg_permissions(self):
        os.system("chmod 600 {}/credentials/config.json".format(self.configuration_dir))
    
    def read_contents(self):
        with open("{}/credentials/config.json".format(self.configuration_dir)) as fp:
            return json.load(fp)

    def make_user_config(self) -> None:
        cu = self.currently_logged_in()[0]

        username = input("Starbucks Username: ")
        password = getpass()

        sec_question_one = input("2FA Question 1: ")
        sec_one = getpass("2FA Question 1 Answer: ")

        sec_question_two = input("2FA Question 2: ")
        sec_two = getpass("2FA Question 2 Answer: ")
        tz = os.popen("timedatectl status | awk '/Time zone/ {print $3}'").read().strip()
        location = input("Store location: ")

        payload = {
            "username": username,
            "password": password,
            "name": cu.capitalize(),
            "sec_one_question": sec_question_one,
            "sec_one_answer": sec_one,
            "sec_two_question": sec_question_two,
            "sec_two_answer": sec_two,
            "timezone": tz,
            "store_location": location
        }

        with open("{}/credentials/config.json".format(self.configuration_dir), "w") as fp:
            json.dump(payload, fp)

        self.chg_permissions()
        jay = json_parser.jsonparser(self.read_contents())
        sudo_execute().swap_user(cu)


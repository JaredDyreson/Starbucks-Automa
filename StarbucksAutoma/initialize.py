#!/usr/bin/env python3.8

import os
from getpass import getpass
from StarbucksAutoma.exceptions import *
import json
import subprocess
from sudo_execute.sudo_execute import sudo_execute

import packaging.version
import pathlib
from StarbucksAutoma.version import __version__ as __sbversion__
from StarbucksAutoma.event_handler import GoogleEventHandler

"""
This portion must be run as root to ensure that file permissions are properly set
We run as root, then change permissions to 600, which is read and write by owner
We are also assuming that the user is running either Linux or MacOS.
Timezone support is not included for Windows, please consult
the list of timezones dumped from timedatectl on the StarbucksAutoma wiki
"""

VERSION = packaging.version.parse(__sbversion__)
STATE_PATH = pathlib.Path("/etc/StarbucksAutoma/state.json")
CONFIG_PATH = pathlib.Path("/etc/StarbucksAutoma/credentials/config.json")

"""
Pulled from the Tuffix project
ORIGINAL AUTHOR: Kevin Wortman
"""

# Configuration defined at build-time. This is a class so that we can
# unit test with dependency injection.
class BuildConfig:
    # version: packaging.Version for the currently-running tuffix
    # state_path: pathlib.Path holding the path to state.json
    def __init__(self,
                 version,
                 state_path):
        if not (isinstance(version, packaging.version.Version) and
                isinstance(state_path, pathlib.Path) and
                state_path.suffix == '.json'):
            raise ValueError
        self.version = version
        self.state_path = state_path

DEFAULT_BUILD_CONFIG = BuildConfig(VERSION, STATE_PATH)

class State:
    # build_config: a BuildConfig object
    # version: packaging.Version for the StarbucksAutoma version that created this state
    def __init__(self, build_config, version, configured):
        if not (isinstance(build_config, BuildConfig) and
                isinstance(version, packaging.version.Version) and
                isinstance(configured, bool)):
            raise ValueError
        self.build_config = build_config
        self.version = version
        self.is_configured = configured

    # Write this state to disk.
    def write(self):
        with open(self.build_config.state_path, 'w') as f:
            document = {
                'version' : str(self.version),
                'configured' : self.is_configured
            }
            json.dump(document, f)

# Reads the current state.
# build_config: A BuildConfig object.
# raises EnvironmentError if there is a problem.
def read_state(build_config):
    if not isinstance(build_config, BuildConfig):
        raise ValueError
    try:
        with open(build_config.state_path) as f:
            document = json.load(f)
            return State(build_config,
                         packaging.version.Version(document['version']),
                         document['configured'])
    except OSError:
        raise EnvironmentError('state file not found, you must run $ starbucksautoma init')
    except json.JSONDecodeError:
        raise EnvironmentError('state file JSON is corrupted')
    except packaging.version.InvalidVersion:
        raise EnvironmentError('version number in state file is invalid')
    except KeyError:
        raise EnvironmentError('state file JSON is missing required keys')
    except ValueError:
        raise EnvironmentError('state file JSON has malformed values')


"""
End Pull
"""

class initializer():
    def __init__(self, build_config):
        if not(isinstance(build_config, BuildConfig)):
            raise ValueError

        self.build_config = build_config
        self.configuration_dir = "/etc/StarbucksAutoma"
        self.sub_dirs = ["configuration",
                        "credentials",
                        "release_builds",
                        "work_schedules"]
        self.ensure_nix()
        self.ensure_root()
        self.ensure_utils()

    def ensure_root(self):
        if(os.getuid() != 0):
            raise EnviornmentException("Run as root")

    def ensure_nix(self):
        if(os.name == "nt"):
            raise EnviornmentException("Windows not supported")

    def ensure_utils(self):
        utilities = ["timedatectl", "awk"]
        for utility in utilities:
            try:
                if(subprocess.run(['which', utility], stdout=subprocess.DEVNULL).returncode != 0):
                    raise EnvironmentError("command {} cannot be found, is this system running systemd?".format(utility))
            except FileNotFoundError:
                raise EnvironmentError("no `which` found, please install")

    def currently_logged_in(self) -> list:
        return [user for user in subprocess.check_output(["users"], encoding="utf-8").split('\n') if user]

    def make_conf_structure(self) -> None:
        if(not os.path.exists(self.configuration_dir)):
            os.mkdir(self.configuration_dir)
        for path in self.sub_dirs:
            os.mkdir(os.path.join(self.configuration_dir, path))

    def chg_permissions(self):
        os.system("chmod 600 {}".format(CONFIG_PATH))
    
    def read_contents(self):
        with open(CONFIG_PATH) as fp:
            return json.load(fp)

    def make_user_config(self) -> None:
        state = read_state(self.build_config)   
        if(state.is_configured):
            raise EnvironmentError("StarbucksAutoma is already configured")

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
            "sec_question_one": sec_question_one,
            "sec_one_answer": sec_one,
            "sec_question_two": sec_question_two,
            "sec_two_answer": sec_two,
            "timezone": tz,
            "store_location": location
        }

        with open(CONFIG_PATH, "w") as fp:
            json.dump(payload, fp)

        self.chg_permissions()
        GoogleEventHandler()

        new_state = State(self.build_config,
                          self.build_config.version,
                          True)
        new_state.write()

        sudo_execute().swap_user(cu)


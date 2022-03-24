"""Driver code for starbucksautoma"""

import os
import json
import time

# Check if you are running as root or normal user
# match os.getuid():
# case num if num > 0:
# raise PermissionError("you must run this as root")

from StarbucksAutoma.constants import PORTAL_URL, default_driver, WEEKS_IN_THE_FUTURE, CONFIG_PATH

with open(CONFIG_PATH, "r", encoding="utf-8") as fil_ptr:
    # Read in configuration data and load it into environment variables (as root)
    # These go away once the process is killed
    os.environ |= json.load(fil_ptr)

from StarbucksAutoma.driver_utils import PortalDriver
from StarbucksAutoma.event_handler import GoogleEventHandler

GOOGLE = GoogleEventHandler()

PORTAL_DRIVER = PortalDriver(default_driver(), PORTAL_URL)
PORTAL_DRIVER.run()
PORTAL_DRIVER.go_to_landing_page()

# for _ in range(0, WEEKS_IN_THE_FUTURE):
    # # Run the program to note the next three weeks
    # time.sleep(1.5)  # wait for the page to load so duplicate events are not present

    # if not (events := PORTAL_DRIVER.siphon_requests()):
        # break
    # for event in events:
        # GOOGLE.add_event(event=event)

    # PORTAL_DRIVER.go_to_next_week()

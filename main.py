"""Driver code for starbucksautoma"""

import typing
import os

# from StarbucksAutoma.driver_utils import PortalDriver
# from StarbucksAutoma.constants import PORTAL_URL_TESTING, default_driver
# from StarbucksAutoma.event_handler import GoogleEventHandler

# GOOGLE = GoogleEventHandler()


# Check if you are running as root or normal user
match os.getuid():
    case num if num > 0:
        raise PermissionError("you must run this as root")

# PORTAL_DRIVER = portal_driver(default_driver(), PORTAL_URL_TESTING)
# PORTAL_DRIVER.run()


# for event in PORTAL_DRIVER.scrape_page():
    # GOOGLE.add_event(event)

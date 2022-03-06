"""Driver code for starbucksautoma"""

import typing

from StarbucksAutoma.driver_utils import portal_driver
from StarbucksAutoma.constants import PORTAL_URL_TESTING, default_driver
from StarbucksAutoma.event_handler import GoogleEventHandler

GOOGLE = GoogleEventHandler()

# PORTAL_DRIVER = portal_driver(default_driver(), PORTAL_URL_TESTING)
# PORTAL_DRIVER.run()


# for event in PORTAL_DRIVER.scrape_page():
    # GOOGLE.add_event(event)

# PORTAL_DRIVER.kill_marionette()

from StarbucksAutoma.driver_utils import portal_driver
from StarbucksAutoma.constants import PORTAL_URL_TESTING, default_driver

PORTAL_DRIVER = portal_driver(default_driver(), PORTAL_URL_TESTING)
PORTAL_DRIVER.run()

elements = PORTAL_DRIVER.scrape_page()

print(stuff)

PORTAL_DRIVER.kill_marionette()

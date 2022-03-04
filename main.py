from StarbucksAutoma.driver_utils import portal_driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import time

headless_ = Options()
headless_.add_argument('--no-sandbox')
headless_.headless = False
driver = webdriver.Firefox(options=headless_)
driver.get("file:///home/jared/Downloads/my_portal/PartnerPortalDocker/ExamplePortal/index.html")

PORTAL_DRIVER = portal_driver(driver)

# PORTAL_DRIVER.load_inner_html_page()

stuff =  PORTAL_DRIVER.scrape_page()
print(stuff)

PORTAL_DRIVER.kill_marionette()

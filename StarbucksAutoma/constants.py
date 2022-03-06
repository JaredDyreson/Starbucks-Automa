"""All constants pertaining to the StarbucksAutoma project"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pathlib

PORTAL_URL = "https://starbucks-wfmr.jdadelivers.com/retail"
PORTAL_URL_TESTING = "file:///home/jared/Downloads/my_portal/PartnerPortalDocker/ExamplePortal/index.html"

PAY_RATE = 17.67

TOKEN_PATH = pathlib.Path("/etc/StarbucksAutoma/credentials/token.pickle")
CREDENTIALS_PATH = pathlib.Path("/etc/StarbucksAutoma/credentials/credentials.json")

TIMEZONE = ""
LOCATION = ""

UTC_OFFSET = "-08:00" # FIXME: this needs to change if it is DST or even a different timezone

def default_driver() -> webdriver.Firefox:
    """Generate a default driver"""

    headless_ = Options()
    headless_.add_argument('--no-sandbox')
    headless_.headless = True
    return webdriver.Firefox(options=headless_)
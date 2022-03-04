"""All constants pertaining to the StarbucksAutoma project"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

PORTAL_URL = "https://starbucks-wfmr.jdadelivers.com/retail"
PORTAL_URL_TESTING = "file:///home/jared/Downloads/my_portal/PartnerPortalDocker/ExamplePortal/index.html"

PAY_RATE = 17.67

def default_driver() -> webdriver.Firefox:
    """Generate a default driver"""

    headless_ = Options()
    headless_.add_argument('--no-sandbox')
    headless_.headless = True
    return webdriver.Firefox(options=headless_)

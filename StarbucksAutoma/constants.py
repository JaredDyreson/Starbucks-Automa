"""All constants pertaining to the StarbucksAutoma project"""

import pathlib

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

from pyvirtualdisplay import Display

PORTAL_URL = "https://starbucks-wfmr.jdadelivers.com/retail"
PORTAL_URL_TESTING = "file:///home/jared/Downloads/my_portal/PartnerPortalDocker/ExamplePortal/index.html"

PAY_RATE = 17.67
WEEKS_IN_THE_FUTURE = 3

TOKEN_PATH = pathlib.Path(
    "/home/jared/Applications/StarbucksAutoma/credentials/token.pickle"
)
CREDENTIALS_PATH = pathlib.Path(
    "/home/jared/Applications/StarbucksAutoma/credentials/client-secret.json"
)
TOKEN_JSON_PATH = pathlib.Path(
    "/home/jared/Applications/StarbucksAutoma/credentials/token.json"
)

CONFIG_PATH = pathlib.Path(
    "/home/jared/Applications/StarbucksAutoma/configuration/configuration.json"
)


def default_driver() -> webdriver.Chrome:
    """Generate a default driver"""

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # headless_.add_argument("--headless")

    # chromeOptions = webdriver.ChromeOptions()
    # chromeOptions.add_argument("--headless")  # this
    # chromeOptions.add_argument("--disable-gpu")

    # chromeOptions.add_argument("--remote-debugging-port=9222")  # this

    driver = webdriver.Chrome(
        # executable_path="/home/jared/Downloads/chromedriver",
        options=options,
        seleniumwire_options={
            "disable_encoding": True,
            "request_storage": "memory",
            "request_storage_max_size": 1,
        },
    )
    driver.scopes = [
        "https://starbucks-wfmr.jdadelivers.com/retail/data/wfmess/api/v1-beta1/mySchedules/.*"
    ]
    return driver

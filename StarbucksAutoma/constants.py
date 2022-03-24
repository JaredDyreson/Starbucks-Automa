"""All constants pertaining to the StarbucksAutoma project"""

import pathlib

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

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

    headless_ = Options()
    headless_.add_argument("--no-sandbox")
    headless_.add_argument("--headless")

    capabilities = webdriver.DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = webdriver.Chrome(
        desired_capabilities=capabilities,
        options=headless_,
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

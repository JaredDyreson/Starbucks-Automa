"""Chrome webdriver helper functions"""

import typing
import datetime
import time
import json
import os
import pickle

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from StarbucksAutoma.event_packet import EventPacket


def get_projected_week(input_string: str) -> typing.List[datetime.datetime]:
    """
    Given a string representation of a week,
    return a seven item long list of datetime objects with no time attached
    @param input_string : representation of the week
    @return typing.List[datetime.datetime] : all of the datetime objects
    """

    begin, end = map(
        lambda x: datetime.datetime.strptime(x, "%m/%d/%Y"), input_string.split(" - ")
    )

    return [begin + datetime.timedelta(days=i) for i in range((end - begin).days)]


class PortalDriver:
    """Object to replicate the human element of opening a browser"""

    def __init__(self, driver, url: str):
        self.driver = driver
        self.url = url

    def __del__(self):
        """When the object goes out of scope, kill it and clean up"""
        self.driver.quit()

    def run(self) -> None:
        """Start the driver"""

        self.driver.get(self.url)

    def get_embedded_page(self) -> str:
        """
        Return the embedded page in the portal that will allow access to the schedule
        """

        return self.driver.find_element_by_css_selector(
            "iframe[class='x-component x-fit-item x-component-default']"
        ).get_attribute("src")

    def find_partner_password_field(self):
        """
        Find and fill te final password field for login
        Returns clickable submit button on the page
        """

        field, button = map(
            self.driver.find_element_by_css_selector,
            (
                "#ContentPlaceHolder1_MFALoginControl1_PasswordView_tbxPassword",
                "input[type='submit']",
            ),
        )
        field.send_keys(os.environ.get("STAR_password"))
        button.click()

    def find_partner_username(self):
        """
        Find and fille the username field  for login
        Retuns a clickable submit button on the page
        """

        self.wait_for_element(
            "#ContentPlaceHolder1_MFALoginControl1_UserIDView_txtUserid"
        )

        field, button = map(
            self.driver.find_element_by_css_selector,
            (
                "#ContentPlaceHolder1_MFALoginControl1_UserIDView_txtUserid",
                "input[type='submit']",
            ),
        )
        field.send_keys(os.environ.get("STAR_username"))
        button.click()

    def find_two_factor_auth(self):
        """
        Find and fill the two factor authentication portion for login
        Returns clickable submit button on the page
        """

        question, input_field, button = map(
            self.driver.find_element_by_css_selector,
            (
                "#ContentPlaceHolder1_MFALoginControl1_KBARegistrationView_lblKBQ1",
                "#ContentPlaceHolder1_MFALoginControl1_KBARegistrationView_tbxKBA1",
                "#ContentPlaceHolder1_MFALoginControl1_KBARegistrationView_btnSubmit",
            ),
        )

        input_field.send_keys(
            os.environ.get("STAR_sec_one_answer")
            if question.text == os.environ.get("STAR_sec_one_question")
            else os.environ.get("STAR_sec_two_answer")
        )

        button.click()

    def go_to_landing_page(self):
        """Navigate to the schedule landing page"""

        print("[+] Finding and filling username field....")
        self.wait_for_element("span[class='sbuxheadertext']")
        self.find_partner_username()

        print("[+] Finding and filling in two factor authentication...")
        self.wait_for_element("span[class='bodytext lblKBQIndicator lblKBQIndicator1']")
        self.find_two_factor_auth()

        time.sleep(1)  # there's this annoying pin message we can just wait out

        print("[+] Finding and filling in password field...")
        self.wait_for_element("a[id='sbuxForgotPasswordURL']")
        self.find_partner_password_field()
        self.wait_for_element("img[class='x-img rp-redprairie-logo x-img-default']")

        self.driver.get(self.get_embedded_page())
        time.sleep(2)

    def go_to_next_week(self):
        """Navigate to the next week on the webpage"""

        self.driver.find_element_by_css_selector(
            "span[id='button-1029-btnIconEl']"
        ).click()

    def wait_for_element(self, selector: str, delay=40):
        """Given a CSS Selector, wait for the element to appear"""

        WebDriverWait(self.driver, delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def siphon_requests(self) -> typing.List[EventPacket]:
        """Listen to outbound requests to the server and note them"""

        container = []

        for request in self.driver.requests:
            _dict = json.loads(request.response.body)

            days_working = filter(
                lambda x: not bool(x["daysInPast"]) and x["payScheduledShifts"],
                _dict["days"],
            )

            for day in days_working:
                # Use this to calculate the total time working along with pay

                # total_work_time = day["netScheduledHours"]
                for shift in day["payScheduledShifts"]:
                    if shift["borrowedSite"]:
                        # TODO: note what the adress is and change `LOCATION`

                        print("oops")

                    start, end = map(
                        lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S"),
                        map(shift.get, ("start", "end")),
                    )
                    coverage_type = shift["job"]["name"]
                    container.append(
                        EventPacket(start, end, f"Jared's Work ({coverage_type})")
                    )

        return container

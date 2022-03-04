"""Firefox webdriver helper functions"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os

import typing
import datetime

from StarbucksAutoma.event_packet import EventPacket
from StarbucksAutoma.constants import PORTAL_URL_TESTING as portal_url

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


class portal_driver:
    def __init__(self, driver, url: str):
        self.driver = driver
        self.url = url

    def run(self) -> None:
        """Start the driver"""

        self.driver.get(self.url)

    @property
    def current_week(self) -> str:
        """Find the current week selected in the navigation menu"""

        return self.driver.find_element_by_css_selector(
            "#textfield-1026-inputEl"
        ).get_attribute("value")

    @property
    def work_week(self) -> typing.List[str]:
        """
        Get a list of web driver elements that contain days working

        @return typing.List[str] : contents of each field to be parsed
        """

        return [
            element.text
            for element in self.driver.find_elements_by_xpath(
                '//*[contains(@class,"x-grid-cell x-grid-td x-grid-cell-headerId-gridColumn")]'
            )[:7]
        ]

    def scrape_page(self) -> typing.List[EventPacket]:
        container: typing.List[EventPacket] = []

        for element, corresponding in zip(
            self.work_week, get_projected_week(self.current_week)
        ):
            if element.strip():
                match element.split("\n"):
                    case [time, coverage, hours]:
                        print("coverage")
                    case [time, other_message]:
                        # conditionally add but mark as unknown
                        print("called off")
                    case _:
                        raise Exception("malformed data")

                start, end = map(
                    lambda x: datetime.datetime.combine(corresponding, x),
                    map(
                        lambda x: datetime.datetime.strptime(x, "%I:%M %p").time(),
                        time.split(" - "),
                    ),
                )

                container.append(EventPacket(start, end))

        return container

    def load_inner_html_page(self):
        """
        Load the sub page of the portal that will allow access to the schedule
        """

        try:
            sub_html_link = self.driver.find_element_by_css_selector(
                "iframe[class='x-component x-fit-item x-component-default']"
            ).get_attribute("src")
            print(sub_html_link)
            # self.driver.get(sub_html_link)
            # sleep(8)
        except NoSuchElementException:
            pass

    def find_partner_password_field(self):
        """
        Find and fille the final password field for login
        Returns clickable submit button on the page
        """

        password_field = self.driver.find_element_by_css_selector(
            "input[type='password']"
        )
        password_field.send_keys(self.jp.getjsonkey("password"))
        return self.driver.find_element_by_css_selector("input[type='submit']")

    def fill_and_submit_password_field(self):
        self.find_partner_password_field().click()

    def find_partner_username(self):
        """
        Find and fille the username field  for login
        Retuns a clickable submit button on the page
        """

        try:
            username_field = self.driver.find_element_by_css_selector(
                "input[class='textbox txtUserid']"
            )
        except NoSuchElementException:
            sleep(4)
            username_field = self.driver.find_element_by_css_selector(
                "input[class='textbox txtUserid']"
            )
        username_field.send_keys(self.jp.getjsonkey("username"))
        return self.driver.find_element_by_css_selector("input[type='submit']")

    def fill_and_submit_username_field(self):
        self.find_partner_username().click()

    def find_two_factor_auth(self):
        """
        Find and fill the two factor authentication portion for login
        Returns clickable submit button on the page
        """

        security_question = self.driver.find_element_by_css_selector(
            "span[class='bodytext lblKBQ lblKBQ1']"
        )
        security_question_field = self.driver.find_element_by_css_selector(
            "input[class='textbox tbxKBA tbxKBA1']"
        )
        security_button = self.driver.find_element_by_css_selector(
            "input[type='submit']"
        )

        if security_question.text == self.jp.getjsonkey("sec_question_one"):
            security_question_field.send_keys(self.jp.getjsonkey("sec_one_answer"))
        else:
            security_question_field.send_keys(self.jp.getjsonkey("sec_two_answer"))
        return security_button

    def go_to_landing_page(self):
        print("[+] Loading portal login page....")
        self.driver.get(portal_url)

        print("[+] Finding and filling username field....")
        self.wait_for_element("span[class='sbuxheadertext']")
        self.fill_and_submit_username_field()

        print("[+] Finding and filling in two factor authentication...")
        self.wait_for_element("span[class='bodytext lblKBQIndicator lblKBQIndicator1']")
        self.fill_and_submit_two_factor_auth()

        print("[+] Finding and filling in password field...")
        self.wait_for_element("a[id='sbuxForgotPasswordURL']")
        self.fill_and_submit_password_field()
        self.wait_for_element("img[class='x-img rp-redprairie-logo x-img-default']")

    def go_to_next_week(self):
        self.driver.find_element_by_css_selector(
            "span[id='button-1029-btnIconEl']"
        ).click()

    def fill_and_submit_two_factor_auth(self):
        self.find_two_factor_auth().click()

    def wait_for_element(self, selector: str, delay=40):
        WebDriverWait(self.driver, delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def kill_marionette(self):
        self.driver.quit()
        os.remove("geckodriver.log")

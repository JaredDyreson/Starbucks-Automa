#!/usr/bin/env python3.5

# Webdriver helper functions and usage message

from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
def usage(programName):
    # Usage information
    print("Usage: "+programName.replace("./","")+"\n-c|--cache\trun but only save to disk\n-s|--scheduler\taffect main calendar\n-v|--verbose\tprint to the screen everything")
    quit()

def waitForPageToLoad(driver, wait, action, text=None):
    wait.until(lambda webpageloaded: ec.title_is("{}".format(text)))
def findUserName(driver, parser):
    try:
        driver.find_element_by_name("ctl00$ContentPlaceHolder1$MFALoginControl1$UserIDView$txtUserid").send_keys(parser.getjsonkey(key="username"))
    except NoSuchElementException:
            time.sleep(4)
            driver.find_element_by_name("ctl00$ContentPlaceHolder1$MFALoginControl1$UserIDView$txtUserid").send_keys(parser.getjsonkey(key="username"))
    return driver.find_element_by_id("ContentPlaceHolder1_MFALoginControl1_UserIDView_btnSubmit")

def findTwoFAQuestion(driver, parser):
    security_question = driver.find_element_by_id("ContentPlaceHolder1_MFALoginControl1_KBARegistrationView_lblKBQ1")
    security_question_box1 = driver.find_element_by_name("ctl00$ContentPlaceHolder1$MFALoginControl1$KBARegistrationView$tbxKBA1")
    security_button = driver.find_element_by_name("ctl00$ContentPlaceHolder1$MFALoginControl1$KBARegistrationView$btnSubmit")
    if(security_question.text == "What city were you born in?"):
        security_question_box1.send_keys(parser.getjsonkey(key="hometown"))
    elif(security_question.text == "What is your favorite hobby?"):
        security_question_box1.send_keys(parser.getjsonkey(key="hobby"))
    return security_button
def findFinalPassword(driver, parser):
    final_password = driver.find_element_by_id("ContentPlaceHolder1_MFALoginControl1_PasswordView_tbxPassword")
    final_password.send_keys(parser.getjsonkey(key="password"))
    return driver.find_element_by_name("ctl00$ContentPlaceHolder1$MFALoginControl1$PasswordView$btnSubmit")


from selenium import webdriver
from os import environ
import argparse

LOGIN_PAGE = "https://nj.myaccount.pseg.com/user/login"
LOGOUT_PAGE = "https://nj.myaccount.pseg.com/user/logout"
READING_DATE_XPATH = '//p[@class="f19-med-cnd next-meter-reading"]'
# TODO: read user and pass from env variable
if environ.has_key("PSEG_USERNAME"):
    USERNAME = environ.get("PSEG_USERNAME")
else:
    print("ERROR: set username with ENV:PSEG_USERNAME")
    exit(1)
if environ.has_key("PSEG_PASSWORD"):
    PASSWORD = environ.get("PSEG_PASSWORD")
else:
    print("ERROR: set password with ENV:PSEG_PASSWORD")
    exit(1)

driver = webdriver.Chrome()
driver.get(LOGIN_PAGE)
# TODO: wrap in try and catch all errors - send a screenshot if passed login
driver.find_element_by_id("username").send_keys(USERNAME)
driver.find_element_by_id("password").send_keys(PASSWORD)
driver.find_element_by_id("submit").click()
# TODO: wait for page to load
reading_date = driver.find_element_by_xpath(READING_DATE_XPATH).text
# TODO: send message to slack
print(reading_date)

driver.get(LOGOUT_PAGE)
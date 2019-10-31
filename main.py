#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import environ
import argparse
from slackclient import SlackClient
import logging
from datetime import timedelta
from datetime import datetime
import time


LOGIN_PAGE = "https://nj.myaccount.pseg.com/user/login"
LOGOUT_PAGE = "https://nj.myaccount.pseg.com/user/logout"
READING_DATE_XPATH = '//p[@class="f19-med-cnd next-meter-reading"]'
USERNAME_FIELD_ID = "username"
PASSWORD_FIELD_ID = "password"
SUBMIT_BUTTON_ID = "submit"


class Pseg():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.chromeDriver()

    def chromeDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def login(self):
        logging.info("navigating to login page")
        self.driver.get(LOGIN_PAGE)
        logging.info("entering username")
        self.driver.find_element_by_id(USERNAME_FIELD_ID).send_keys(self.username)
        logging.info("entering password")
        self.driver.find_element_by_id(PASSWORD_FIELD_ID).send_keys(self.password)
        logging.info("clicking submit")
        self.driver.find_element_by_id(SUBMIT_BUTTON_ID).click()
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, READING_DATE_XPATH)))
        logging.info("login complete")

    def getReadingDate(self):
        self.reading_date = self.driver.find_element_by_xpath(
            READING_DATE_XPATH).text
        logging.info("scraped reading date: %s" % self.reading_date)
        return self.reading_date

    def logout(self):
        self.driver.get(LOGOUT_PAGE)
        logging.info("logged out")

    def quit(self):
        logging.info("quiting webdriver")
        self.driver.quit()


class Slack():
    def __init__(self, api_token, channel_id):
        self.channel_id = channel_id
        self.client = SlackClient(api_token)

    def send(self, msg, scheduled=False):
        msg_txt = "Your next PSE&G meter reading will be on " + msg
        if scheduled:
            ttime = datetime.strptime(msg, "%m/%d/%Y") + timedelta(days=-1.5)
            self.client.api_call(
                "chat.scheduleMessage",
                channel=self.channel_id,
                text=msg_txt,
                post_at=time.mktime(ttime.timetuple())
            )
        else:
            self.client.api_call(
                "chat.postMessage",
                channel=self.channel_id,
                text=msg_txt
            )

    def error(self, msg):
        msg_txt = "Failed to get next PSE&G meter reading date. ```{}```".format(msg)
        self.client.api_call(
            "chat.postMessage",
            channel=self.channel_id,
            text=msg_txt
        )

def parseArgs():
    parser = argparse.ArgumentParser(
        description='Lookup next meter reading date')
    parser.add_argument(
        '--username', default=environ.get("PSEG_USERNAME"),
        help="pseg.com account username (overrides PSEG_USERNAME)"
    )
    parser.add_argument(
        '--password', default=environ.get("PSEG_PASSWORD"),
        help="pseg.com account password (overrides PSEG_PASSWORD)"
    )
    parser.add_argument(
        "--slack-api-token", default=environ.get("SLACK_API_TOKEN"),
        help="slack api token (overrides SLACK_API_TOKEN)"
    )
    parser.add_argument(
        "--slack-channel", default=environ.get("SLACK_CHANNEL"),
        help="slack channel to send messages to (overrides SLACK_CHANNEL)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="DEFAULT: False"
    )
    args = parser.parse_args()
    if not args.username or not args.password:
        exit(parser.print_help())
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    return args

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:[%(levelname)s]:%(message)s"
    )
    args = parseArgs()
    slack = Slack(args.slack_api_token, args.slack_channel)
    client = Pseg(args.username, args.password)
    try:
        client.login()
        reading_date = client.getReadingDate()
        if args.slack_api_token and args.slack_channel:
            slack.send(reading_date, True)
        client.logout()
    except Exception as e:
        logging.critical(e)
        slack.error(e)
    finally:
        client.quit()

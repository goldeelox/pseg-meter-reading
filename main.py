#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import environ
import argparse
from slackclient import SlackClient
import logging

LOGIN_PAGE = "https://nj.myaccount.pseg.com/user/login"
LOGOUT_PAGE = "https://nj.myaccount.pseg.com/user/logout"
READING_DATE_XPATH = '//p[@class="f19-med-cnd next-meter-reading"]'


class Pseg():
    def __init__(self):
        self.args = self.parseArgs()
        self.driver = webdriver.Chrome()

    def parseArgs(self):
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

    def login(self):
        logging.info("navigating to login page")
        self.driver.get(LOGIN_PAGE)
        logging.info("entering username")
        self.driver.find_element_by_id(
            "username").send_keys(self.args.username)
        logging.info("entering password")
        self.driver.find_element_by_id(
            "password").send_keys(self.args.password)
        logging.info("clicking submit")
        self.driver.find_element_by_id("submit").click()
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, READING_DATE_XPATH)))
        logging.info("login complete")

    def getReadingDate(self):
        self.reading_date = self.driver.find_element_by_xpath(
            READING_DATE_XPATH).text
        logging.info("scraped reading date: %s" % self.reading_date)
        if self.args.slack_api_token and self.args.slack_channel:
            slacky(self.reading_date, self.args.slack_api_token,
                   self.args.slack_channel)

    def logout(self):
        self.driver.get(LOGOUT_PAGE)
        logging.info("logged out")

    def quit(self):
        logging.info("quiting webdriver")
        self.driver.quit()


def slacky(msg, api_token, channel_id):
    client = SlackClient(api_token)
    client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text="Your next PSE&G meter reading will be on " + msg
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:[%(levelname)s]:%(message)s"
    )
    client = Pseg()
    try:
        client.login()
        client.getReadingDate()
        client.logout()
    except Exception as e:
        logging.critical(e)
    finally:
        client.quit()

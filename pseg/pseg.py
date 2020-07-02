from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

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
        self.driver.find_element_by_id(
            USERNAME_FIELD_ID).send_keys(self.username)
        logging.info("entering password")
        self.driver.find_element_by_id(
            PASSWORD_FIELD_ID).send_keys(self.password)
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

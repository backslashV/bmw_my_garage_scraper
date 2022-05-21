from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import os
import telegram_send

# supress web driver manager logs
os.environ['WDM_LOG'] = '0'

CHROME_BINARY_PATH = 'C:\\Program Files\\Google\Chrome\\Application\\chrome.exe'

USERNAME = "example@email.com"
PASSWORD = "your_my_garage_password"

MY_GARAGE_URL = "https://mygarage.bmwusa.com/"
NUM_INPUT_TAGS = 2
CREDENTIALS_TAG = "input"
LOGIN_BUTTON_CLASS_NAME = ".custom-button.__b.primary"
VEHICLE_VIN_CLASS_NAME = "mbg__vehicle-vinprod"
VEHICLE_PRODUCTION_STATUS_TAG = "div"
VEHICLE_PRODUCTION_STATUS_CLASS_NAME = "mbg__vehicle-status"
TIMEOUT = 10 # in seconds

def main():
    global driver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.binary_location = CHROME_BINARY_PATH
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(MY_GARAGE_URL)
    except Exception as ex:
        cleanUpAndExit(ex)

    # wait for the login screen to fully load
    implicitWaitForPageLoad(By.CSS_SELECTOR, LOGIN_BUTTON_CLASS_NAME)
    # log in
    performLogin(USERNAME, PASSWORD)
    # wait for my garage to fully load
    implicitWaitForPageLoad(By.CLASS_NAME, VEHICLE_VIN_CLASS_NAME)
    # save the previous status
    prevStatus = getPreviousStatus()
    # fetch the production status
    productionStatus = getProductionStatus(BeautifulSoup(driver.page_source, 'html.parser'))
    # write production status to file
    writeProductionStatusToFile(productionStatus)
    # send updates via telegram
    sendStatusViaTelegram(prevStatus, productionStatus)
    print(productionStatus)
    cleanUpAndExit()

def getStatusFileName():
    return os.path.dirname(os.path.realpath(__file__)) + "\status.txt"

def getPreviousStatus():
    fileName = getStatusFileName()
    if not os.path.exists(fileName):
        return ""
    with open(fileName, "r") as file:
        return file.read()

def writeProductionStatusToFile(status):
    with open(getStatusFileName(), "w") as file:
        file.write(status)

def sendStatusViaTelegram(prevStatus, newStatus):
    # only send updates if the new status is different
    if prevStatus != newStatus:
        message = prevStatus + "->" + newStatus
        telegram_send.send(messages=["`" + message + "`"], parse_mode="markdown")

def getProductionStatus(html):
    statusWithExtras = html.find_all(VEHICLE_PRODUCTION_STATUS_TAG,
            {"class": VEHICLE_PRODUCTION_STATUS_CLASS_NAME})[0]
    return statusWithExtras.text.split(":  ", 1)[1]

def performLogin(username, password):
    # find the username and password fields
    inputTags = driver.find_elements(By.TAG_NAME, CREDENTIALS_TAG)
    if len(inputTags) < NUM_INPUT_TAGS:
        cleanUpAndExit("Not all input tags were found. Quitting...")
    usernameField = inputTags[0]
    passwordField = inputTags[1]
    loginButton = driver.find_elements(By.CSS_SELECTOR, LOGIN_BUTTON_CLASS_NAME)[0]
    usernameField.send_keys(username)
    passwordField.send_keys(password)
    loginButton.click()

def implicitWaitForPageLoad(locator, locatorValue):
    try:
        WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_any_elements_located((locator,
                locatorValue)))
    except:
        cleanUpAndExit("implicitWaitForPageLoad timed out - locatorValue: " + locatorValue)

def cleanUpAndExit(message = ""):
    driver.quit()
    exit(message)

if __name__ == "__main__":
  main()
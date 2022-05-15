from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import os

# supress web driver manager logs
os.environ['WDM_LOG'] = '0'

CHROME_BINARY_PATH = 'C:\\Program Files\\Google\Chrome\\Application\\chrome.exe'

USERNAME = "example@email.com"
PASSWORD = "your_my_garage_password"

MY_GARAGE_URL = "https://mygarage.bmwusa.com/"
VEHICLE_VIN_CLASS_NAME = "mbg__vehicle-vinprod"
VEHICLE_PRODUCTION_STATUS_CLASS_NAME = "mbg__vehicle-status"
TIMEOUT = 10 # in seconds

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
    exit(ex)

# find the username and password fields
inputTags = driver.find_elements(By.TAG_NAME, "input")
usernameField = inputTags[0]
passwordField = inputTags[1]
loginButton = driver.find_elements(By.CSS_SELECTOR, ".custom-button.__b.primary")[0]

usernameField.send_keys(USERNAME)
passwordField.send_keys(PASSWORD)
loginButton.click()

# wait for the url to become my garage
try:
    WebDriverWait(driver, TIMEOUT).until(EC.url_matches(MY_GARAGE_URL))
except Exception as ex:
    exit("Timeout occured waiting for My Garage URL")

# wait for my garage to fully load
try:
    WebDriverWait(driver, TIMEOUT).until(EC.text_to_be_present_in_element((By.CLASS_NAME, VEHICLE_VIN_CLASS_NAME), "PRODUCTION #: "))
except:
    exit("My Garage took too long to load. Quitting...")

html = BeautifulSoup(driver.page_source, 'html.parser')
productionStatus = html.find_all("div", {"class": VEHICLE_PRODUCTION_STATUS_CLASS_NAME})[0]

print(productionStatus.text.split(":  ", 1)[1])
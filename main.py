from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import validators
import time
from colorama import init
from termcolor import colored

init()

activities = ["Solo Dungeon",
              "Solo Dungeon (Stage 2)",
              "Solo Dungeon (Timerun)",
              "Party Dungeon",
              "Party Dungeon Stage 2",
              "Dungeon Points",
              "Personal",
              "PvP"]

def navigateTo(driver, activity):
    select = Select(driver.find_element_by_id("inputGroupSelect04"))
    go = driver.find_element_by_id("activity-select-btn")
    select.select_by_value(activity)
    go.click()
    

class wait_for_non_checking(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = EC._find_element(driver, self.locator)
            element_text = element.text.strip()
            if element_text != "Checking...":
                return element
        except StaleElementReferenceException:
            return False
   
def printCategoryInfo(driver, links, activityName):
    activities = driver.find_elements_by_xpath("//div[@class='activities']//li")
    print(f"\n---- {activityName} ----")
    for activity in activities:
        wait = WebDriverWait(activity, 10)
        claimBtn = wait.until(wait_for_non_checking((By.TAG_NAME, "button")))
        descriptionBtn = activity.find_element_by_tag_name("i")
        descriptionBtn.click()
        title = activity.find_element_by_class_name("activities-title")
        points = activity.find_elements_by_class_name("currency-amount")[0]
        coins = activity.find_elements_by_class_name("currency-amount")[1]
        description = activity.find_element_by_tag_name("p")
        descriptionText = description.text[:-46] if activityName == 'Personal' else description.text
        color = "white"
        if claimBtn.text == 'CLAIM':
            links.append(claimBtn.get_attribute("data-action-url"))
            color = 'green'
        elif claimBtn.text == 'CLAIMED':
            color = 'cyan'
        info = colored(f"{title.text} | points: {points.text} | coins: {coins.text} => {descriptionText}", color)
        print(info)
    return links

def claimLinks(driver, links):
    for link in links:
        url = "https://client.cabal.one" + link
        driver.get(url)
        result = driver.find_element_by_xpath("//body")
        print(result.text)

def claimLoginReward(driver):
    loginReward = driver.find_element_by_id("take-login-gift")
    loginReward.click()
    driver.refresh()

def claimActivityRewards(driver):
    links = []
    for activity in activities:
        navigateTo(driver, activity)
        links = printCategoryInfo(driver, links, activity)
    claimLinks(driver, links)

def teardownDriver(driver):
    print("---- done ----")
    driver.quit()

def setUpDriver():
    options = Options()
    options.add_argument('log-level=3')
    try:
        options.headless = True if sys.argv[1] == 'headless' else False
    except:
        options.headless = False
    driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
    driver.implicitly_wait(10)
    driver.maximize_window()
    return driver

def getPanel(url, driver):
    driver.get(url)
    return printCurrencies(driver)

def claimBoxesRewards(driver, points):
    boxes = ["/site/claim-gift?type=gold",
             "/site/claim-gift?type=silver",
             "/site/claim-gift?type=bronze"]
    removeQuantity = -3 if points >= 240 else -2 if points >= 120 else -1 if points >= 80 else -3 
    boxes = boxes[:removeQuantity]
    print(f"boxes => {boxes}")
    claimLinks(driver, boxes)
    
def printCurrencies(driver):
    points = driver.find_element_by_xpath("//div[@class='first-currency']")
    coins = driver.find_element_by_id("current-coins")
    print(f"points: {points.text}")
    print(f"coins: {coins.text}")
    return int(points.text)

def getUrl():
    valid = False
    while not valid: 
        url = input("url?\n")
        valid = validators.url(url)
    return url

def main():
    while True:
        url = getUrl()
        start_time = time.time()
        driver = setUpDriver()
        points = getPanel(url, driver)
        claimLoginReward(driver)
        claimActivityRewards(driver)
        claimBoxesRewards(driver, points)
        getPanel(url, driver)
        teardownDriver(driver)
        execution_time = round(time.time() - start_time, 2)
        print(execution_time)

try:
    main()
except Exception:
    pass
    main()


    


import csv
import random
import requests
import traceback
from selenium import webdriver 
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import os
import time
from selenium_stealth import stealth
import pandas as pd
def log_to_telegram(message: str):
    print(message)
    try:
        requests.get(f"https://api.telegram.org/bot1831551869:AAG-onhWuV_JXwsb6goT8ge4StCNEKCmmyI/sendMessage?chat_id=664831837&text={message}")
    except Exception:
        print(str(traceback.format_exc()))

def main():
    chromedriver_autoinstaller.install(cwd=True)
    driver_options = Options()
    driver_options.add_argument("start-minimized")
    driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver_options.add_argument('--profile-directory=Default')
    driver_options.add_argument(f"--user-data-dir={os.getcwd()}/profile/")
    driver_options.add_argument("--disable-gpu")
    close_msg = "Unable to evaluate script: disconnected: not connected to DevTools\n"
    driver = webdriver.Chrome(options=driver_options)
    stealth(driver,
        user_agent='DN',
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    try:
        df = pd.read_csv("./data.csv", index_col=0, encoding='utf8')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(
            {
                "Username": [],
                "URL": [],
                "Status": [],
            }
        )
        df.to_csv("./data.csv",index=False, quoting=csv.QUOTE_NONNUMERIC)
    try:
        while True:
            driver.get(f"https://www.duolingo.com/profile/MaximilianGaedig/following")
            ActionChains(driver).pause(10).perform()
            try:
                friend_anchors = driver.find_elements_by_css_selector('.xdvY3 a')
                for anchorEl in friend_anchors:
                    username = anchorEl.find_element_by_xpath('.//div[2]/h3').text
                    if not (df["Username"] == username).any():
                        df = df.append({"Username":username,"URL":anchorEl.get_attribute('href'),"Status":"Found"},ignore_index=True)
                df.to_csv("./data.csv",index=False, quoting=csv.QUOTE_NONNUMERIC)
            except Exception:
                    log_to_telegram("EXCEPTION:\n" + str(traceback.format_exc()))
            ActionChains(driver).pause(1).perform()
            try:
                if driver.find_element_by_xpath('/html/body').text == "Too many requests":
                    log_to_telegram("TOO MANY REQUESTS!!")
                    ActionChains(driver).pause(1200).perform()
            except Exception:
                pass
            for index, row in df.iterrows():
                if row["Status"] == "Found":
                    try:
                        driver.get(row["URL"])
                        ActionChains(driver).pause(1).perform()
                        if not driver.current_url == "https://www.duolingo.com/errors/404.html":
                            following_element = WebDriverWait(driver, 10).until(
                                expected_conditions.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        '//*[@id="root"]/div/div[2]/div/div[1]/div[2]/div/button/div',
                                    )
                                )
                            )
                            following = following_element.text
                            if following == "FOLLOWING":
                                following_element.click()
                                log_to_telegram(row["Username"] + " Unfollowed")
                                df["Status"][index] = "Unfollowed"
                            else:
                                log_to_telegram(row["Username"] + " NotFollowing")
                                df["Status"][index] = "NotFollowing"
                        else:
                            log_to_telegram(row["Username"] + " 404")
                            df["Status"][index] = "404"
                    except Exception:
                        log_to_telegram("EXCEPTION:\n" + str(traceback.format_exc()))
                        try:
                            if driver.find_element_by_xpath('/html/body').text == "Too many requests":
                                log_to_telegram("TOO MANY REQUESTS!!")
                                ActionChains(driver).pause(1200).perform()
                        except Exception:
                            pass
                    df.to_csv("./data.csv",index=False, quoting=csv.QUOTE_NONNUMERIC)
    finally: 
        driver.quit()
        df.to_csv("./data.csv",index=False, quoting=csv.QUOTE_NONNUMERIC)

main()
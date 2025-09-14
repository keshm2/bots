from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()),
options = options)

driver.get("https://www.youtube.com/")

search = driver.find_element(By.XPATH,'//input[@id = "search"]')

while True:
    print("Q for quit")
    print("Enter search term: ")
    query = input()
    
    if query == "Q" or query == "q":
        break
    else:
        try:
            driver.maximize_window()
            time.sleep(1)
            search.send_keys(query)
            search.send_keys(Keys.RETURN)
            time.sleep(3)
            search.clear()
        except Exception as error:
            print(error)
            driver.quit()
        except KeyboardInterrupt as e:
            continue


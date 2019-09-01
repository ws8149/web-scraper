import multiprocessing
import time
import timeit
# import csv
# import re
# import time
# import sys
import requests
from collections import deque

from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent


# Setup Chrome display
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
ua = UserAgent()



# Only change the executable_path to your path. Leave the chrome_options.
user = ua.random
print(user)
options.add_argument(f'user-agent={user}')
driver = webdriver.Chrome(options=options, executable_path=r'C:\Scrape\chromedriver.exe')




driver.get("https://www.uwa.edu.au/study/courses-and-careers/find-a-course")

element = driver.find_element_by_class_name("results-action-load-more")

time.sleep(10)
driver.quit()
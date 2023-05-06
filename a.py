from scrape import *
from selenium import webdriver
chrome_driver_path = "/Users/username/Downloads/chromedriver" # replace with your own path  
# Scrapes Google Flights for round-trip JFK to IST, leave July 15, 2023, return July 25, 2023.
# driver=webdriver.Chrome(chrome_driver_path)
result = Scrape("JFK", "IST", "2023-07-15", "2023-07-25")
# Obtain data + info
flights = result.data # outputs as a Pandas dataframe
origin = result.origin # "JFK"
dest = result.dest # "IST"
date_leave = result.date_leave # "2023-07-15"
date_return = result.date_return # "2023-07-25"
print(flights)
print(result)
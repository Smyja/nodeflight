from scrape import *
from selenium import webdriver
# Scrapes Google Flights for round-trip JFK to IST, leave July 15, 2023, return July 25, 2023.

#Example Usage
result = Scrape("Lagos", "Casablanca", "2023-07-15", "2023-07-25")
flights = result.data
origin = result.origin
dest = result.dest
date_leave = result.date_leave
date_return = result.date_return
for item in flights:
  company_name = item['companyName']
  price = item['price']
  layover = item['layover']
  airportLeave = item['airportLeave']
  airportArrive = item['airportArive']
  duration = item['duration']
  description = item['description']
  thumbnail = item['thumbnail']
  website = item['website']
  print("Company Name:", company_name)
  print("Logo URL:", thumbnail)
  print("Price:", price)
  print("Layover(s):", layover)
  print("Airport Leave:", airportLeave)
  print("Airport Arrive:", airportArrive)
  print("Duration of Flight:", duration)
  print("Description:", description)
  print("Website:", website)

"""
For Replit Bounty by @Smyja 
Made by @TechAarya
"""
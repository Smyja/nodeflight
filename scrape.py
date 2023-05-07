'''/****************************************************************************************************************************************************************
  Written by Kaya Celebi, April 2023
****************************************************************************************************************************************************************/'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm
import re


__all__ = ['Scrape', '_Scrape']

class _Scrape:

	def __init__(self):
		self._origin = None
		self._dest = None
		self._date_leave = None
		self._date_return = None
		self._data = None

	def __call__(self, *args):
		if len(args) == 4:
			self._set_properties(*args)
			self._data = self._scrape_data()
			obj = self.clone()
			obj.data = self._data
			return obj
		else:
			self._set_properties(*(args[:-1]))
			obj = self.clone()
			obj.data = args[-1]
			return obj

	def __str__(self):
		return "{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
			dl = self._date_leave,
			dr = self._date_return,
			org = self._origin,
			dest = self._dest
		)

	def __repr__(self):
		return "{n} RESULTS FOR:\n{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
			n = self._data.shape[0],
			dl = self._date_leave,
			dr = self._date_return,
			org = self._origin,
			dest = self._dest
		)

	def clone(self):
		obj = _Scrape()
		obj._set_properties(
			self._origin, self._dest, self._date_leave, self._date_return
		)
		return obj

	'''
		Set properties upon scraper called.
	'''
	def _set_properties(self, *args):
		(
			self._origin, self._dest, self._date_leave, self._date_return
		) = args

	@property
	def origin(self):
		return self._origin

	@origin.setter
	def origin(self, x : str) -> None:
		self._origin = x

	@property
	def dest(self):
		return self._dest

	@dest.setter
	def dest(self, x : str) -> None:
		self._dest = x

	@property
	def date_leave(self):
		return self._date_leave

	@date_leave.setter
	def date_leave(self, x : str) -> None:
		self._date_leave = x

	@property
	def date_return(self):
		return self._date_return

	@date_return.setter
	def date_return(self, x : str) -> None:
		self._date_return = x

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, x):
		self._data = x

	'''
		Scrape the object
	'''
	def _scrape_data(self):
		url = self._make_url()
		return self._get_results(url)


	def _make_url(self):
		return 'https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{org}%20on%20{dl}%20through%20{dr}'.format(
			dest = self._dest,
			org = self._origin,
			dl = self._date_leave,
			dr = self._date_return
		)

	def _get_results(self, url):
		results = _Scrape._make_url_request(url)

		flight_info = _Scrape._get_info(results)
		partition = _Scrape._partition_info(flight_info)

		return _Scrape._parse_columns(partition, self._date_leave, self._date_return)

	@staticmethod
	def _get_driver():
		driver = None
		try:
			driver = webdriver.Chrome()
		except:
			raise Exception(
				'''Appropriate ChromeDriver version not found.\n
				Make sure Chromedriver is downloaded with appropriate version of Chrome.\n
				In Chrome, Go to Settings --> About Chrome to find version.\n 
				Visit https://chromedriver.chromium.org and download matching ChromeDriver version.
				'''
			)

	@staticmethod
	def _make_url_request(url):
		driver = webdriver.Chrome()
		driver.get(url)
	
		# Waiting and initial XPATH cleaning
		WebDriverWait(driver, timeout = 10).until(lambda d: len(_Scrape._get_flight_elements(d)) > 9)
		results = _Scrape._get_flight_elements(driver)
		
		driver.quit()

		return results

	@staticmethod
	def _get_flight_elements(driver):
		elements = driver.find_elements(by = By.XPATH, value = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[@class = "pIav2d"]')
		result = []
		for el in elements:
			result.extend( el.text.split('\n'))
			x = re.search(r"url[^);]+", el.find_element(by=By.XPATH, value=".//div/div[2]/div/div[2]/div[1]/div").get_attribute("style"))
			result.append(  x.group()[4:].replace("\\",""))
		return result

	@staticmethod
	def _get_info(result):
		info = []
		for r in result:
			if  'price' not in r.lower() and 'prices' not in r.lower() and 'other' not in r.lower() and ' – ' not in r.lower():
				info += [r]

		return info

	@staticmethod
	def _partition_info(info):
		i, grouped = 0, []
		while i < len(info) - 1:
			j = i + 2
			end = -1
			while j < len(info):
				if _Scrape._end_condition(info[j]):
					end = j
					break
				j += 1

			if end == -1:
				break
			grouped += [info[i:end]]
			i = end

		return grouped

	@staticmethod
	def _end_condition(x):
		if len(x) < 2:
			return False

		if x[-2] == "+":
			x = x[:-2]

		if x[-2:] == 'AM' or x[-2:] == 'PM':
			return True
		return False

	@staticmethod
	def _parse_columns(grouped, date_leave, date_return):
		flight_data = []

		for g in grouped:
			i_diff = 0

			depart_time = g[0]
			arrival_time = g[1]

			i_diff += 1 if 'Separate tickets booked together' in g[2] else 0

			airline = g[2 + i_diff]
			travel_time = g[3 + i_diff]
			origin = g[4 + i_diff].split('–')[0]
			dest = g[4 + i_diff].split('–')[1]

			num_stops = 0 if 'Nonstop' in g[5 + i_diff] else int(g[5 + i_diff].split('stop')[0])

			stop_time = None if num_stops == 0 else (g[6 + i_diff].split('min')[0] if num_stops == 1 else None)
			stop_location = None if num_stops == 0 else (g[6 + i_diff].split('min')[1] if num_stops == 1 and 'min' in g[6 + i_diff] else [g[6 + i_diff].split('hr')[1] if 'hr' in g[6 + i_diff] and num_stops == 1 else g[6 + i_diff]])

			i_diff += 0 if num_stops == 0 else 1

			if g[6 + i_diff] != '–':
				co2_emission = float(g[6 + i_diff].replace(',','').split(' kg')[0])
				emission = 0 if g[7 + i_diff] == 'Avg emissions' else int(g[7 + i_diff].split('%')[0])
				price = float(re.sub('[^0-9.]', '', g[8 + i_diff]))
				trip_type = g[9 + i_diff]
			else:
				co2_emission = None
				emission = None
				price = float(re.sub('[^0-9.]', '', g[7 + i_diff]))
				trip_type = g[8 + i_diff]

			flight_data.append({
				"thumbnail": g[-1], # Need a different method to scrape airline logo URLs
				"companyName": airline,
				"description": f"Leaves {origin} at {depart_time} on {date_leave} and arrives at {dest} at {arrival_time} on {date_return}.",
				"duration": travel_time,
				"airportLeave": origin,
				"airportArive": dest,
				"layover": f"Layover (1 of {num_stops}) is a {stop_time} layover at {stop_location}." if num_stops > 0 else "Nonstop",
				"emisions": f"Carbon emissions estimate: {co2_emission} kilograms. {emission}% emissions " if co2_emission and emission else "",
				"price": f"NGN{price}"
			})
		df = pd.DataFrame(flight_data)
		df.to_json("h.json", orient='records')
		return flight_data


Scrape = _Scrape()
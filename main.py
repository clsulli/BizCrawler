"""
Lead Generation Software
TODO Page Scraper, Page Insights API

Clint Sullivan
4/9/2018
All Rights Reserved
"""

from BizCrawler import leadGenerator
from BizCrawler import detailer
import json
import requests

pageSpeedsAPI = "AIzaSyCpX0WJZBIlYg8FHT4GkGB1ZgGABEQzepE"

detail = detailer()

api_key = 'AIzaSyCpX0WJZBIlYg8FHT4GkGB1ZgGABEQzepE'  # Add API key. Found here: https://console.developers.google.com/apis/credentials/key/
base = 'http://example.com'
locale_code = 'en_US'

speedRes = detail.get_insights_json(api_key=api_key, device_type="desktop", local=locale_code, page_url="https://www.procryoplus.com")
print(speedRes)

lg = leadGenerator()
lg.find("Doctors", "62025", 4)





"""
Lead Generation Software
TODO Page Scraper, Page Insights API

Clint Sullivan
4/9/2018
All Rights Reserved
"""

from BizCrawler import finder
from BizCrawler import detailer

fb = finder()
dt = detailer()

sampleURL = "https://www.yelp.com/biz/simmering-james-md-maryville-3?osq=Doctors"

query = fb.query("Doctors", "62025")
detail = dt.detail(sampleURL)





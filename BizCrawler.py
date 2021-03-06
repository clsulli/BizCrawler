from lxml import html
import csv
import requests
# from exceptions import ValueError
# from time import sleep
import re
import argparse
import urllib.parse
import json
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

#TODO Multithreading
#TODO Email Scraping

class leadGenerator:
    def __init__(self):
        self.finder = finder()
        self.detailer = detailer()

    def find(self, search_query, zipcode, numOfPages):
        pool = ThreadPool(10)

        yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s" % (search_query, zipcode, 0)
        possiblePages = self.finder.totalPages(yelp_url)

        if numOfPages > possiblePages:
            numOfPages = possiblePages
            print("Too many pages!  Setting to highest amount of possible pages: %s", numOfPages)

        file = self.finder.query(search_query=search_query, place=zipcode, numOfPages=numOfPages)
        csvFile = csv.DictReader(open(file, 'r'), delimiter=',', quotechar='"')
        listings = []

        for line in csvFile:
            listings.append(line['url'])

        # for listing in range(len(listings)):
        #     self.detailer.detail(listings[listing])
        pool.map(self.detailer.detail, listings)
        pool.close()
        pool.join()

class finder:
    """
    Class for finding businesses based on a search query from user
    """
    def totalPages(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers, verify=False).text
        parser = html.fromstring(response)
        total_results = parser.xpath("//span[@class='pagination-results-window']//text()")
        total_results = ''.join(e for e in total_results[-1] if e.isalnum())
        total_results = total_results.split('of')
        total_results = int(total_results[-1])
        print(total_results)
        total_pages = divmod(total_results, 10)[0]

        return total_pages

    def parse(self, url):
        """
        Takes a url structured for yelp and then scrapes the web page for business listings.  Each listing scraped is
        saved as a dict.  Each dict is appended to a list containing each business listing.

        :param url: url is a url structured for a yelp search
        :return: a dict of the scraped data.
        """
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers, verify=False).text
        parser = html.fromstring(response)
        listing = parser.xpath("//li[@class='regular-search-result']")

        scraped_datas = []

        for results in listing:
            # raw_position = results.xpath(".//span[@class='indexed-biz-name']/text()")
            raw_name = results.xpath(".//span[@class='indexed-biz-name']/a//text()")
            #raw_ratings = results.xpath(".//div[contains(@class,'rating-large')]//@title")
            # raw_review_count = results.xpath(".//span[contains(@class,'review-count')]//text()")
            # raw_price_range = results.xpath(".//span[contains(@class,'price-range')]//text()")
            # category_list = results.xpath(".//span[contains(@class,'category-str-list')]//a//text()")
            # raw_address = results.xpath(".//address//text()")
            # is_reservation_available = results.xpath(".//span[contains(@class,'reservation')]")
            # is_accept_pickup = results.xpath(".//span[contains(@class,'order')]")
            url = "https://www.yelp.com"+results.xpath(".//span[@class='indexed-biz-name']/a/@href")[0]
            name = ''.join(raw_name).strip()
            # position = ''.join(raw_position).replace('.','')
            # cleaned_reviews = ''.join(raw_review_count).strip()
            # reviews =  re.sub("\D+","",cleaned_reviews)
            # categories = ','.join(category_list)
            #cleaned_ratings = ''.join(raw_ratings).strip()
            # if raw_ratings:
            #     ratings = re.findall("\d+[.,]?\d+",cleaned_ratings)[0]
            # else:
            #     ratings = 0
            # price_range = len(''.join(raw_price_range)) if raw_price_range else 0
            # address  = ' '.join(' '.join(raw_address).split())
            # reservation_available = True if is_reservation_available else False
            # accept_pickup = True if is_accept_pickup else False
            data={
                'business_name':name,
                # 'rank':position,
                # 'review_count':reviews,
                # 'categories':categories,
                # 'rating':ratings,
                # 'address':address,
                # 'reservation_available':reservation_available,
                # 'accept_pickup':accept_pickup,
                # 'price_range':price_range,
                'url':url
            }
            scraped_datas.append(data)
        return scraped_datas

    def query(self, search_query, place, numOfPages):
        """
        Performs a query by creating a yelp structured url based on the parameter values.  The url(s) are then processed
        by parse().  The listings are then written to a csv file for viewing.

        :param search_query: A query such as "Doctors", "Best Restraunts" etc.
        :param place: A zip code of the area you want to search in.
        :return: A csv file of business listings.
        """
        place = place
        search_query = search_query
        parseList = []

        for i in range(1, numOfPages+1):
            startIdx = i*10
            yelp_url  = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,startIdx)
            print ("Retrieving :",yelp_url)
            parseList.append(self.parse(yelp_url))

        print ("Writing data to output file")
        with open("Listings/scraped_yelp_results_for_%s_%s.csv"%(search_query, place),"w") as fp:
            fieldnames= ['business_name','rank','review_count','categories','rating','address','reservation_available','accept_pickup','price_range','url']
            writer = csv.DictWriter(fp,fieldnames=fieldnames)
            writer.writeheader()
            for parse in parseList:
                for data in parse:
                    writer.writerow(data)

        return "Listings/scraped_yelp_results_for_%s_%s.csv"%(search_query, place)

class detailer:

    def get_insights_json(self, page_url, local, device_type, api_key):
        url = 'https://www.googleapis.com/pagespeedonline/v2/runPagespeed?url=' + page_url + '&filter_third_party_resources=true&locale=' + local + '&screenshot=false&strategy=' + device_type + '&key=' + api_key
        # print "Getting :: " + url
        r = requests.get(url)
        return_code = r.status_code
        return_text = r.text
        return_json = json.loads(return_text)

        return return_json

    def rateSite(self, url):
        api_key = 'xxxx'  # Add API key. Found here: https://console.developers.google.com/apis/credentials/key/
        locale_code = 'en_US'

        speedRes = self.get_insights_json(api_key=api_key, device_type="desktop", local=locale_code, page_url=url)
        speed = speedRes['ruleGroups']['SPEED']['score']
        return speed

    def parse(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers, verify=False).text
        parser = html.fromstring(response)
        print("Parsing the page")
        raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
        details_table = parser.xpath("//div[@class='short-def-list']//dl")
        raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
        raw_address = parser.xpath('//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
        raw_wbsite_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
        raw_ratings = parser.xpath("//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")

        info = []
        for details in details_table:
            raw_description_key = details.xpath('.//dt//text()')
            raw_description_value = details.xpath('.//dd//text()')
            description_key = ''.join(raw_description_key).strip()
            description_value = ''.join(raw_description_value).strip()
            info.append({description_key: description_value})

        # ratings_histogram = []
        # for ratings in rating_histogram:
        #     raw_rating_key = ratings.xpath(".//th//text()")
        #     raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
        #     rating_key = ''.join(raw_rating_key).strip()
        #     rating_value = ''.join(raw_rating_value).strip()
        #     ratings_histogram.append({rating_key: rating_value})

        name = ''.join(raw_name).strip()
        phone = ''.join(raw_phone).strip()
        address = ' '.join(' '.join(raw_address).split())
        # health_rating = ''.join(raw_health_rating).strip()
        # price_range = ''.join(raw_price_range).strip()
        # claimed_status = ''.join(raw_claimed).strip()
        # reviews = ''.join(raw_reviews).strip()
        # category = ','.join(raw_category)
        cleaned_ratings = ''.join(raw_ratings).strip()

        if raw_wbsite_link:
            decoded_raw_website_link = urllib.parse.unquote(raw_wbsite_link[0])
            website = re.findall("biz_redir\?url=(.*)&website_link", decoded_raw_website_link)[0]
        else:
            website = ''

        if raw_ratings:
            ratings = re.findall("\d+[.,]?\d+", cleaned_ratings)[0]
        else:
            ratings = 0

        if website != '':
            score = self.rateSite(website)
        else:
            score = 0

        data = {#'working_hours': working_hours,
                #'info': info,
                #'ratings_histogram': ratings_histogram,
                'name': name,
                'phone': phone,
                'ratings': ratings,
                'address': address,
                #'health_rating': health_rating,
                #'price_range': price_range,
                #'claimed_status': claimed_status,
                #'reviews': reviews,
                #'category': category,
                'website': website,
                'score': score,
                #'latitude': latitude,
                #'longitude': longitude,
                'url': url
                }
        return data

    def detail(self, url):
        scraped_data = self.parse(url)
        yelp_id = url.split('/')[-1]
        yelp_id = ''.join(e for e in yelp_id if e.isalnum())
        with open("Json/scraped_data_%s.json" % yelp_id, 'w') as fp:
            json.dump(scraped_data, fp, indent = 4)

   # if __name__ == "__main__":
   #     argparser = argparse.ArgumentParser()
   #     argparser.add_argument('url', help='yelp bussiness url')
   #     args = argparser.parse_args()
   #     url = args.url
   #     scraped_data = parse(url)
   #     yelp_id = url.split('/')[-1]
   #     with open("scraped_data_%s.json" % yelp_id, 'w') as fp:
   #         json.dump(scraped_data, fp, indent=4)

from lxml import html
import csv
import requests
# from exceptions import ValueError
# from time import sleep
import re
import argparse
import urllib.parse
import json

class finder:

   def parse(self, url):
      headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
      response = requests.get(url, headers=headers, verify=False).text
      parser = html.fromstring(response)
      print ("Parsing the page")
      listing = parser.xpath("//li[@class='regular-search-result']")
      total_results = parser.xpath("//span[@class='pagination-results-window']//text()")
      scraped_datas=[]
      print(total_results)
      for results in listing:
         raw_position = results.xpath(".//span[@class='indexed-biz-name']/text()")
         raw_name = results.xpath(".//span[@class='indexed-biz-name']/a//text()")
         raw_ratings = results.xpath(".//div[contains(@class,'rating-large')]//@title")
         raw_review_count = results.xpath(".//span[contains(@class,'review-count')]//text()")
         raw_price_range = results.xpath(".//span[contains(@class,'price-range')]//text()")
         category_list = results.xpath(".//span[contains(@class,'category-str-list')]//a//text()")
         raw_address = results.xpath(".//address//text()")
         is_reservation_available = results.xpath(".//span[contains(@class,'reservation')]")
         is_accept_pickup = results.xpath(".//span[contains(@class,'order')]")
         url = "https://www.yelp.com"+results.xpath(".//span[@class='indexed-biz-name']/a/@href")[0]

         name = ''.join(raw_name).strip()
         position = ''.join(raw_position).replace('.','')
         cleaned_reviews = ''.join(raw_review_count).strip()
         reviews =  re.sub("\D+","",cleaned_reviews)
         categories = ','.join(category_list)
         cleaned_ratings = ''.join(raw_ratings).strip()
         if raw_ratings:
            ratings = re.findall("\d+[.,]?\d+",cleaned_ratings)[0]
         else:
            ratings = 0
         price_range = len(''.join(raw_price_range)) if raw_price_range else 0
         address  = ' '.join(' '.join(raw_address).split())
         reservation_available = True if is_reservation_available else False
         accept_pickup = True if is_accept_pickup else False
         data={
               'business_name':name,
               'rank':position,
               'review_count':reviews,
               'categories':categories,
               'rating':ratings,
               'address':address,
               'reservation_available':reservation_available,
               'accept_pickup':accept_pickup,
               'price_range':price_range,
               'url':url
         }
         scraped_datas.append(data)
      return scraped_datas

   def query(self, search_query, place):
      place = place
      search_query = search_query
      startIdx = str(0)
      parseList = []
      yelp_url  = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,startIdx)
      print ("Retrieving :",yelp_url)
      parseList.append(self.parse(yelp_url))
      startIdx = str(10)
      yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,startIdx)
      parseList.append(self.parse(yelp_url))
      print ("Writing data to output file")
      with open("scraped_yelp_results_for_%s_%s.csv"%(search_query, place),"w") as fp:
         fieldnames= ['business_name','rank','review_count','categories','rating','address','reservation_available','accept_pickup','price_range','url']
         writer = csv.DictWriter(fp,fieldnames=fieldnames)
         writer.writeheader()
         for parse in parseList:
            for data in parse:
               writer.writerow(data)

# if __name__=="__main__":
#    argparser = argparse.ArgumentParser()
#    argparser.add_argument('place',help = 'Location/ Address/ zip code')
#    search_query_help = """Available search queries are:\n
#                      Restaurants,\n
#                      Breakfast & Brunch,\n
#                      Coffee & Tea,\n
#                      Delivery,
#                      Reservations"""
#    argparser.add_argument('search_query',help = search_query_help)
#    args = argparser.parse_args()
#    place = args.place
#    search_query = args.search_query
#    startIdx = str(0)
#    parseList = []
#    yelp_url  = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,startIdx)
#    print ("Retrieving :",yelp_url)
#    parseList.append(parse(yelp_url))
#    startIdx = str(10)
#    yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,startIdx)
#    parseList.append(parse(yelp_url))
#    print ("Writing data to output file")
#    with open("scraped_yelp_results_for_%s.csv"%(place),"w") as fp:
#       fieldnames= ['business_name','rank','review_count','categories','rating','address','reservation_available','accept_pickup','price_range','url']
#       writer = csv.DictWriter(fp,fieldnames=fieldnames)
#       writer.writeheader()
#       for parse in parseList:
#          for data in parse:
#             writer.writerow(data)

class detailer:

   def parse(self, url):
      # url = "https://www.yelp.com/biz/frances-san-francisco"
      headers = {
         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
      response = requests.get(url, headers=headers, verify=False).text
      parser = html.fromstring(response)
      print("Parsing the page")
      raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
      raw_claimed = parser.xpath("//span[contains(@class,'claim-status_icon--claimed')]/parent::div/text()")
      raw_reviews = parser.xpath(
         "//div[contains(@class,'biz-main-info')]//span[contains(@class,'review-count rating-qualifier')]//text()")
      raw_category = parser.xpath(
         '//div[contains(@class,"biz-page-header")]//span[@class="category-str-list"]//a/text()')
      hours_table = parser.xpath("//table[contains(@class,'hours-table')]//tr")
      details_table = parser.xpath("//div[@class='short-def-list']//dl")
      raw_map_link = parser.xpath("//a[@class='biz-map-directions']/img/@src")
      raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
      raw_address = parser.xpath('//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
      raw_wbsite_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
      raw_price_range = parser.xpath("//dd[contains(@class,'price-description')]//text()")
      raw_health_rating = parser.xpath("//dd[contains(@class,'health-score-description')]//text()")
      rating_histogram = parser.xpath("//table[contains(@class,'histogram')]//tr[contains(@class,'histogram_row')]")
      raw_ratings = parser.xpath("//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")

      working_hours = []
      for hours in hours_table:
         raw_day = hours.xpath(".//th//text()")
         raw_timing = hours.xpath("./td//text()")
         day = ''.join(raw_day).strip()
         timing = ''.join(raw_timing).strip()
         working_hours.append({day: timing})
      info = []
      for details in details_table:
         raw_description_key = details.xpath('.//dt//text()')
         raw_description_value = details.xpath('.//dd//text()')
         description_key = ''.join(raw_description_key).strip()
         description_value = ''.join(raw_description_value).strip()
         info.append({description_key: description_value})

      ratings_histogram = []
      for ratings in rating_histogram:
         raw_rating_key = ratings.xpath(".//th//text()")
         raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
         rating_key = ''.join(raw_rating_key).strip()
         rating_value = ''.join(raw_rating_value).strip()
         ratings_histogram.append({rating_key: rating_value})

      name = ''.join(raw_name).strip()
      phone = ''.join(raw_phone).strip()
      address = ' '.join(' '.join(raw_address).split())
      health_rating = ''.join(raw_health_rating).strip()
      price_range = ''.join(raw_price_range).strip()
      claimed_status = ''.join(raw_claimed).strip()
      reviews = ''.join(raw_reviews).strip()
      category = ','.join(raw_category)
      cleaned_ratings = ''.join(raw_ratings).strip()

      if raw_wbsite_link:
         decoded_raw_website_link = urllib.parse.unquote(raw_wbsite_link[0])
         website = re.findall("biz_redir\?url=(.*)&website_link", decoded_raw_website_link)[0]
      else:
         website = ''

      if raw_map_link:
         decoded_map_url = urllib.parse.unquote(raw_map_link[0])
         map_coordinates = re.findall("center=([+-]?\d+.\d+,[+-]?\d+\.\d+)", decoded_map_url)[0].split(',')
         latitude = map_coordinates[0]
         longitude = map_coordinates[1]
      else:
         latitude = ''
         longitude = ''

      if raw_ratings:
         ratings = re.findall("\d+[.,]?\d+", cleaned_ratings)[0]
      else:
         ratings = 0

      data = {'working_hours': working_hours,
              'info': info,
              'ratings_histogram': ratings_histogram,
              'name': name,
              'phone': phone,
              'ratings': ratings,
              'address': address,
              'health_rating': health_rating,
              'price_range': price_range,
              'claimed_status': claimed_status,
              'reviews': reviews,
              'category': category,
              'website': website,
              'latitude': latitude,
              'longitude': longitude,
              'url': url
              }
      return data

   def detail(self, url):
       scraped_data = self.parse(url)
       yelp_id = url.split('/')[-1]
       with open("scraped_data_%s.json" % yelp_id, 'w') as fp:
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

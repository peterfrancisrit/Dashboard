#/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import itertools
import re
import json
import urllib3
import pandas as pd
import numpy as np
import time

class CafeScraper:
    ''' Takes a list of websites and scrapes for data
    need to find what is in common with all of these websites.
    It may be necessary to look at common factors but we will start there

    params: websites = list(website_name_0, website_name_1, ... , website_name_n)

    '''

    def __init__(self, websites, conversions):
        self.websites = websites
        self.conversions = conversions
        self.content = {}
        self.euro = {}
        for i, j in zip(websites,conversions):
            self.euro[i] = j


    def getContent(self):
        df = []
        key = 0
        for url in self.websites:
            url_prod = url+'/products.json'
            flag = True
            i = 0
            print(f"URL: {url}")
            while flag:
                try:
                    url_page = url_prod + '?page={}'.format(i)
                    data = requests.get(url_page).json()
                    if data['products'] == []:
                        flag = False
                    else:
                        for entry in data['products']:
                            new_data = entry['variants'][0]
                            new_data['price'] = float(new_data['price']) * self.euro[url]
                            new_data['vendor'] = entry['vendor']
                            new_data['url'] = url
                            new_data['key'] = key
                            try:
                                new_data['bio'] = entry['body_html'].split('<p>')[1]
                                new_data['productType'] = entry['product_type']
                                new_data['type'] = entry['tags'][0]
                                new_data['type_coffee'] = entry['tags'][1]
                                new_data['origin'] = entry['tags'][2]
                            except:
                                pass
                            df.append(new_data)
                    i += 1
                    time.sleep(1)
                except:
                    flag = False
                    break

            time.sleep(1)
            key += 1
        self.products = pd.DataFrame(df)

    def printContent(self):
        print(self.products)

    def cleantype(self):
        clean_data = []
        self.products.type = self.products.type.fillna('')
        for i in self.products.type:
            if 'beans' in i.lower():
                clean_data.append(1)
            elif 'filter' in i.lower():
                clean_data.append(1)
            elif 'espresso' in i.lower():
                clean_data.append(1)
            elif 'blend' in i.lower():
                clean_data.append(1)
            else:
                clean_data.append(0)
        self.products['beans'] = clean_data

    def cleantime(self):
        self.products = self.products.drop('created_at',axis=1)
        self.products['updated_at'] = pd.to_datetime(self.products.updated_at)

    def tocsv(self):
        self.products.to_csv('results.csv',index=False)

import csv
import time
import random
import logging
import requests
import pandas as pd
from datetime import date
from googlesearch import search
from urllib.parse import urlparse, parse_qs

import mysql.connector
from mysql.connector import Error


logging.basicConfig(filename='legitimate_eval_info.log', filemode='a', format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

data_dir = "./"

f = open('url.csv', 'w')
writer = csv.writer(f)
writer.writerow(["url"])
f.close()

def get_googlesearch():
    keywords = []
    with open(data_dir + 'keywords.csv', mode='r') as keywords_file:
        keywords_reader = csv.DictReader(keywords_file)

        for row in keywords_reader:
            keywords.append(row['keyword'])

    types = ['', '', '', '', 'login', 'online', 'bank', 'business', 'cloud', 'login and password', 'signin', 'signup',
             'register', 'forget password', 'recover password', 'pay', 'credit card payment', 'payment',
             'shopping', 'ecommarce']


    for i in range(3):
        url_seen_now = set()
        support_word = random.choice(types)
        if support_word != '' and random.random() < 0.2:
            k = ''
        else:
            k = random.choice(keywords)
        search_query = k + " " + support_word

        for url in search(search_query, tld="com", num=10, stop=10, pause=5):
            same_host = 0
            same_flag = 0

            if urlparse(url).hostname not in url_seen_now:
                url_seen_now.add(urlparse(url).hostname)

            with open(data_dir + 'l-url.data', mode='r') as url_file:
                url_reader = csv.DictReader(url_file, fieldnames=['url'])

                for row in url_reader:
                    if row['url'] == url:
                        same_flag = 1
                    else:
                        if urlparse(row['url']).hostname == urlparse(url).hostname:
                            same_host = same_host + 1

                if (0 == 0):
                    with open(data_dir + 'url.csv', mode='a') as app_url_file:
                        data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        data_writer.writerow([url])
                    with open(data_dir + 'l-url.data', mode='a') as app_url_file:
                        data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        data_writer.writerow([url])

def get_localurls():
    sql = "SELECT url FROM legitimate ORDER BY RAND() LIMIT %s"
    val = (20,)
    cursor.execute(sql, val)

    if (cursor.rowcount > 0):
        result = cursor.fetchall()
        for row in result:
            url = row[0]
            with open(data_dir + 'url.csv', mode='a') as app_url_file:
                data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([url])

    cursor.close()
    connection.close()

choice = random.randint(1, 9)
if choice > 3:
	get_localurls()
else:
	get_googlesearch()

df = pd.read_csv("url.csv")
urlColumn = df['url']

for value in urlColumn.values:
    start = time.time()
    res = requests.post('http://127.0.0.1:5000/moraphishdet', json={"url":value})
    if res.ok:
        end = time.time()
        time_dif = end-start
        action = res.json()['action']
        used_url = res.json()['url']

        url_exists = 0
        with open(data_dir + 'url.data', mode='r') as url_file:
            url_reader = csv.DictReader(url_file, fieldnames=['url'])

            for row in url_reader:
                if row['url'] == used_url:
                    url_exists = 1

        if action >= 0 and action < 3 and url_exists == 0:
            correctness = "correct" if action==0 else "incorrect"
            today = date.today()

            with open(data_dir + 'url.data', mode='a') as app_url_file:
                data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([used_url])

            with open(data_dir + 'eval.csv', mode='a') as app_eval_file:
                data_writer = csv.writer(app_eval_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([today, used_url, 0, action, time_dif, correctness])

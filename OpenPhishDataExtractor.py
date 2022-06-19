import csv
import sys
import time
import random
import logging
import requests
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup # BeautifulSoup is in bs4 package
from googlesearch import search
from urllib.parse import urlparse, parse_qs

import xml.etree.ElementTree as ET
from connection import DBConnection
from pysafebrowsing import SafeBrowsing

logging.basicConfig(filename='open_phish_info.log', filemode='a', format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

data_dir = "./"
google_app_key = ''
googleSafeBrowser = SafeBrowsing(google_app_key)
phishtank_base_url = "https://checkurl.phishtank.com/checkurl/index.php"
phishtank_app_key = ""

def get_google_decision(url):
    google_decision = False
    try:
        google_decision = googleSafeBrowser.lookup_urls([url])[url]['malicious']
    except:
        print("Google error:", sys.exc_info()[1])
    return google_decision

def get_phishtank_decision(url):
    phishtank_decision = False
    try:
        phishtank_decision = PhishTank(url)
    except:
        print("PhishTank error:", sys.exc_info()[1])
    return phishtank_decision

def get_moraphishrepo_decision(url):
    moraphishrepo_decision = False
    try:
        moraphishrepo_decision = MoraPhishRepo(url)
    except:
        print("MoraPhishRepo error:", sys.exc_info()[1])
    return moraphishrepo_decision

def PhishTank(url):
    in_phishtank_database = False
    phishtank_phishing = False

    try:
        r = requests.get(phishtank_base_url + '?url=' + url + '&app_key=' + phishtank_app_key + '&format=json')
        xmlDict = {}
        root = ET.fromstring(r.content)

        for child in root.iter('in_database'):
            in_phishtank_database = True if child.text == 'true' else False

        if in_phishtank_database:
            for child in root.iter('valid'):
                phishtank_phishing = True if child.text == 'true' else False
    except:
        print("PhishTank error:", sys.exc_info()[1])
    return(phishtank_phishing)

def MoraPhishRepo(url):
    phishing_status = False
    connection = DBConnection("moraphishrepo").get_connection()
    cursor = connection.cursor(buffered=True)

    sql = "SELECT * FROM record WHERE url = %s"
    val = (str(url), )
    cursor.execute(sql, val)

    if (cursor.rowcount > 0):
        result = cursor.fetchall()
        if result[0][2] == 1:
            phishing_status = True

    cursor.close()
    return phishing_status

def get_open_phish_data(value):
    google_decision = get_google_decision(value)
    phishtank_decision = get_phishtank_decision(value)
    #moraphishrepo_decision = get_moraphishrepo_decision(value)
    final_decision = 1 if (google_decision or phishtank_decision) else 0

    if final_decision == 0:
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
                correctness = "correct" if action==1 else "incorrect"
                today = date.today()

                with open(data_dir + 'url.data', mode='a') as app_url_file:
                    data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    data_writer.writerow([used_url])

                with open(data_dir + 'eval_2.csv', mode='a') as app_eval_file:
                    data_writer = csv.writer(app_eval_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    data_writer.writerow([today, used_url, 1, action, time_dif, correctness])

URL = 'https://openphish.com/'
content = requests.get(URL)
soup = BeautifulSoup(content.text, 'html.parser')

data = []
contentTable  = soup.find('table') # Use dictionary to pass key : value pair
rows  = contentTable.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

for value in range(1,15):
    same_flag = 0
    with open(data_dir + 'p-url.data', mode='r') as url_file:
        url_reader = csv.DictReader(url_file, fieldnames=['url'])

        for row in url_reader:
            if row['url'] == data[value][0]:
                same_flag = 1
    try:
        if same_flag == 0:
            with open(data_dir + 'p-url.data', mode='a') as app_url_file:
                data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([data[value][0]])
            get_open_phish_data(data[value][0])
    except:
        print("OpenPhish error:", sys.exc_info()[1])

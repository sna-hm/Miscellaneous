import io
import csv
import time
import logging
import requests
import pandas as pd
from datetime import date
from datetime import datetime

logging.basicConfig(filename='phishing_eval_info.log', filemode='a', format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

data_dir = "./"

url="http://data.phishtank.com/data/<<APP_KEY>>/online-valid.csv"
online_verified=requests.get(url).content
df=pd.read_csv(io.StringIO(online_verified.decode('utf-8')))

split = df["submission_time"].str.split("-", n = 2, expand = True)
submission_y = split[0]
submission_m = split[1]
submission_d = split[2].str.split("T", n = 1, expand = True)
submission_h = submission_d[1].str.split(":", n = 1, expand = True)
df.insert(1, "submission_year", submission_y, True)
df.insert(2, "submission_month", submission_m, True)
df.insert(3, "submission_day", submission_d[0], True)
df.insert(4, "submission_hour", submission_h[0], True)
df['submission_year'] = df['submission_year'].astype(int)
df['submission_month'] = df['submission_month'].astype(int)
df['submission_day'] = df['submission_day'].astype(int)
df['submission_hour'] = df['submission_hour'].astype(int)

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year
lastHour = datetime.now().hour - 1

df = df[(df['submission_year'] == currentYear) & (df['submission_month'] == currentMonth) & (df['submission_day'] == currentDay) & (df['submission_hour'] == lastHour)]

urlColumn = df['url']
phishIdColumn = df['phish_id']
count = 0

for value in urlColumn.values:
    same_flag = 0
    with open(data_dir + 'p-url.data', mode='r') as url_file:
        url_reader = csv.DictReader(url_file, fieldnames=['url'])
        for row in url_reader:
            if row['url'] == value:
                same_flag = 1

    if same_flag == 0 and count < 500:
        count = count + 1
        with open(data_dir + 'p-url.data', mode='a') as app_url_file:
                data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow([value])

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
                    
                with open(data_dir + 'eval.csv', mode='a') as app_eval_file:
                    data_writer = csv.writer(app_eval_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    data_writer.writerow([today, used_url, 1, action, time_dif, correctness])

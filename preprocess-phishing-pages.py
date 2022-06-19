## This file is used to fiter unwanted phishing webpages which were there in https://www.fcsit.unimas.my/phishing-dataset during HybridDLM project
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

import codecs
import csv
import os
import re
import shutil
import urllib


data_dir = "/home/subhash/jupyter-notebook/data-extractor/data/"
folder_path = data_dir + 'phishing/'
count = 0
im_list = {"suspended", "available", "loding", "website is inactive", "under maintenance", 
           "warning", "domain for sale", "redirect", "domain is disabled", "suspected", "url", 
           "please wait", "tinyurl", "banned", "suspend", "loading", "redirection", "redirecting", 
           "phishing", "attention required", "not found", "unavailable", "deceptive", "security bypass", 
           "error", "might be a problem", "page not found", "blacklist site", "blacklist", "no longer available",
          "hosting", "free hosting", "not exist"}

im_list_2 = {"website is currently not available", "no longer valid", "autoecole-lauriston.com", 
             "domain is marked as inactive" }

print("Processing... Don't Interrupt")
for subdirList in next(os.walk(folder_path))[1]:
    error = 0
    
    if os.path.exists(folder_path + subdirList):
        url_file_path = folder_path + subdirList + '/URL/URL.txt'
        html_file_path = folder_path + subdirList + '/RAW-HTML/page.html'
        
        with open(url_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, fieldnames=['url'])

            for row in csv_reader:
                url = row['url']
                        
            f = codecs.open(html_file_path, 'r', encoding='utf-8', errors='ignore')
            soup = BeautifulSoup(f)
            
            title_tag = soup.find("title")
            if title_tag is not None:
                title_tag_txt = title_tag.string.strip()
                #print(subdirList + ": " + title_tag_txt)
                if title_tag_txt == "Account Suspended":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Suspected phishing site | Cloudflare":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "This website is currently unavailable.":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Stop! Deceptive page ahead!":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Suspended":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Website Unavailable":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Warning! | There might be a problem with the requested link":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                elif title_tag_txt == "Page not found":
                    print("---->" + subdirList + ": " + url) 
                    error = 1
                    
                for word in im_list:
                    if re.search(r'' + word + '', title_tag_txt.lower()):
                        print("NEW---->" + subdirList + ": " + url) 
                        error = 1
                
                #metaTags = soup.findAll('meta')
                #for meta in metaTags:
                    #if meta.has_attr('content'):
                        #if re.search(r'noindex,nofollow', meta.attrs['content'].lower()):
                                #print("META---->" + subdirList + ": " + url) 
                                #error = 1
                # newly added
                text = soup.find_all(text=True)
                for blkword in im_list_2:
                    for t in text:
                        if t.parent.name not in blacklist:
                            if re.search(r'' + blkword + '', t.lower()):
                                error = 1
                
                body_tag = soup.find("body")
                head_tag = soup.find("head")
                if body_tag is not None:
                    if len(soup.body.contents) > 1:
                        pass
                    else:
                        if head_tag is not None:
                            if len(soup.head.contents) > 2:
                                pass
                            else:
                                print("NO BODY ---->" + subdirList + ": " + url)
                
    if error is 1:
        count = count + 1
        shutil.rmtree(folder_path + subdirList, ignore_errors=False, onerror=None)
    else:
        with open(data_dir + 'p-url-list.data', mode='a') as app_url_file:
            data_writer = csv.writer(app_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)                    
            data_writer.writerow([url])
                                    
print("Done")
print("No of Deleted Folders: " + str(count))
print("No of Remaining Folders: " + str(5000 - count))

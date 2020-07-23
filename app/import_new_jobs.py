import pandas as pd
import numpy as np
import re
import time
import io
import datetime
import random
import os
import glob

import requests as rq
import bs4 as bs4
import json
from pymongo import MongoClient

from feature_extractor import convert_datetime


with open('../config.json') as json_file:
    config = json.load(json_file)


queries = ["data%20scientist"]

NUM_PAGES = 1

locations = ["São%20Paulo%2C%20Brazil",
             "Porto%20Alegre%2C%20Rio%20Grande%20do%20Sul%2C%20Brazil",
             "Europe",
             "England",
             "Ireland",
             "Netherlands",
             'Canada']

url_template = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&pageNum=0&f_TP=1%2C2&start={page}"

client = MongoClient(config['MONGO_URI'])
db = client.get_database('linkedin')
collection = db.jobIds

headers = {
    "User-Agent": "PythonRequests",
}

path = os.path.abspath(os.getcwd())

start = 0
for query in queries:
    for location in locations:
        for page in range(0, NUM_PAGES):
            url = url_template.format(
                query=query, page=page*25, location=location)
            print(f"Downloading {url}")
            response = rq.get(url, headers=headers)
            filename = "{}_{}_{}.html".format(
                query, location, page).replace("%20", "_")
            file_path = os.path.join(path, 'pages', filename)
            with io.open(file_path, "w+", encoding="utf-8") as f:
                f.write(response.text)

            parsed = bs4.BeautifulSoup(response.text)
            job_tags = parsed.findAll("li", class_="result-card")

            time.sleep(random.randint(2, 4))

            # If less than 25 jobs in a page (therefore is the last page) then break
            if len(job_tags) < 25:
                break

new_documents = []

for document in os.listdir(os.path.join(path, 'pages')):

    with io.open("./pages/{}".format(document), "r", encoding="utf-8") as inp:
        page_html = inp.read()

        print(f"Page {document}:")
        parsed = bs4.BeautifulSoup(page_html)

        tags = parsed.findAll("li", class_="result-card")
        for tag in tags:
            item = {'jobId': tag['data-id'], 'loaded': False,
                    'added': datetime.datetime.utcnow()}
            alreadyIn = collection.find_one({"jobId": item['jobId']})
            if not alreadyIn:
                print(f"Adding {item['jobId']}")
                new_documents.append(item)

if len(new_documents):
    collection.insert_many(new_documents)
    print(f"Added {len(new_documents)} new jobs!")

for job in collection.find({'loaded': False}):
    url_template = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jobId}"
    url = url_template.format(jobId=job['jobId'])
    print(url)
    response = rq.get(url)
    with io.open("./jobs/{}.html".format(job['jobId']), "w", encoding="utf-8") as f:
        f.write(response.text)
        job['loaded'] = True
        job['created'] = datetime.datetime.utcnow()
        collection.replace_one({'jobId': job['jobId']}, job)
    time.sleep(random.randint(2, 5))


not_loaded = collection.count_documents({'loaded': False})
loaded_not_parsed = collection.count_documents({'loaded': True, 'title': None})

print(
    f"There are {not_loaded} not loaded jobs and {loaded_not_parsed} still to parse")

for i, job in enumerate(collection.find({'loaded': True, 'title': None})):
    jobId = job['jobId']
    filename = "./jobs/{}.html".format(jobId)

    if not (os.path.exists(filename) and os.path.isfile(filename)):
        print('Could not find html page, setting as not loaded.')
        job['loaded'] = False
        collection.replace_one({'jobId': job['jobId']}, job)
        continue

    with io.open(filename, "r", encoding="utf-8") as f:

        print(f"Job {jobId}:")

        page_html = f.read()
        parsed = bs4.BeautifulSoup(page_html, features="lxml")
        company_a = parsed.findAll("a", class_="topcard__org-name-link")
        if company_a:
            job['company'] = company_a[0].get_text()
        else:
            job['company'] = parsed.findAll(
                "span", class_="topcard__flavor")[0].get_text()
        job['title'] = parsed.findAll(
            "h2", class_="topcard__title")[0].get_text()
        job['city'] = parsed.findAll(
            "span", class_="topcard__flavor topcard__flavor--bullet")[0].contents[0]
        delta_posted = convert_datetime(parsed.findAll("span", class_=[
                                        "topcard__flavor--metadata posted-time-ago__text", "topcard__flavor--metadata posted-time-ago__text posted-time-ago__text--new"])[0].contents[0])
        job['posted'] = job['created'] - delta_posted
        applicants = parsed.findAll(
            "span", class_="topcard__flavor--metadata topcard__flavor--bullet num-applicants__caption")
        if applicants:
            job['applicants'] = int(applicants[0].get_text().split(' ')[0])
        else:
            job['applicants'] = 10
        job['applicants_per_day'] = job['applicants'] / (delta_posted.days + 1)
        job['description'] = parsed.findAll(
            "div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5")[0].get_text()
        job['description_len'] = len(job['description'])
        job_criterion = parsed.findAll(
            "span", class_="job-criteria__text job-criteria__text--criteria")
        job_header = parsed.findAll("h3", class_="job-criteria__subheader")
        for header, value in zip(job_header, job_criterion):
            job[header.get_text()] = value.get_text()

        collection.replace_one({'jobId': job['jobId']}, job)


files = glob.glob('./pages/*')
for f in files:
    os.remove(f)

files = glob.glob('./jobs/*')
for f in files:
    os.remove(f)

total = collection.count_documents({})
print(f"Finished! There are {total} jobs in the database.")

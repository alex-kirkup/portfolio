#from bs4 import BeautifulSoup
#import cloudscraper
import csv
from requests_html import HTMLSession
from urllib.parse import urlencode

API_KEY = '1a7fe6cb-69e1-4f57-bcf3-1f16c148890b'

# John Watson Rooney
# https://github.com/jhnwr/indeed-scraper/blob/main/indeed.py


# https://scrapeops.io/web-scraping-playbook/403-forbidden-error-web-scraping/
# https://pypi.org/project/urllib3/ (urlencode)
def get_proxy_url(url):
    payload = {
        'api_key': API_KEY, 
        'url': url, 
        'bypass': 'cloudflare',
    }
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


def get_data_cloudscraper(session, url):
    r = session.get(get_proxy_url(url))
    #response_temp = scraper.get(url)
    #print("##########################################")
    #print(response_temp.request.headers.get('x-forwarded-for'))
    #response = response_temp.text # scraper.get(url).text
    #print("##########################################")
    #print(response)
    #response_html = BeautifulSoup(response)#, features="html.parser")
    #print("##########################################")
    #print(response_html)
    return r.html.find('ul.pagination-list a[aria-label=Next]'), r.html.find('div.job_seen_beacon')
    #return response_html.find('ul.pagination-list a[aria-label=Next]'), response_html.find('div.job_seen_beacon')


def get_data(session, url):
    r = session.get(get_proxy_url(url))
    return r.html.find('ul.pagination-list a[aria-label=Next]'), r.html.find('div.job_seen_beacon')


def parse_html(session, html):
    job_dict = {
        'title' : html.find('h2 > a')[0].text,
        'link': 'https://uk.indeed.com/viewjob?jk=' + html.find('h2 > a')[0].attrs['data-jk'],
        'companyname': html.find('span.companyName')[0].text,
        'snippet': html.find('div.job-snippet')[0].text.replace('\n', '').strip()
    }

    desc_html = session.get(get_proxy_url(job_dict['link'])).html
    job_dict['description'] = desc_html.find('div.jobsearch-jobDescriptionText')[0].text
        
    try:
        job_dict['salary'] = html.find('div.metadata.salary-snippet-container')[0].text
    except IndexError as err:
        job_dict['salary'] = 'N/A'

    return job_dict


def export(job_list):
    keys = job_list[0].keys()
    with open('results.csv', 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(job_list)


# session = HTMLSession()
# url = 'https://uk.indeed.com/jobs?q=data+scientist&l=London%2C+Greater+London'

# job_list = []

# start = 0
# count = 0
# while count < 3:#True:
#     pagination_url = f'{url}&start={start}' if start else url
#     try:
#         jobs = get_data(session, pagination_url)
#         print("##############################")
#         print(pagination_url)
#         print("##############################")
#         for job in jobs[1]:
#             print(count)
#             job_list.append(parse_html(session, job))
#             print(job_list[-1])
#             print('-------------------------------------')
#             count+=1
#             if count >= 3: break
#         start+=10
        
#     except:
#         break

# export(job_list)

###########################################################################

# NLP USING NLTK

###########################################################################


with open('skills list.csv') as file:
    csv_reader = csv.reader(file)
    skills_list = list(csv_reader)


with open('results.csv') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    dict_reader = csv.DictReader(file, fieldnames=headers)
    job_list = list(dict_reader)


skills_count_dict = {skill[0] : 0 for skill in skills_list}

import nltk

for job in job_list:

    # tokenize the text into words
    tokens = nltk.word_tokenize(job['description'])

    # get the part of speech for each word
    pos_tags = nltk.pos_tag(tokens)

    # extract the nouns from the text
    nouns = set(str(word).lower() for word, pos in pos_tags if pos.startswith('N'))

    for skill in skills_list:
        for alias in skill:
            alias = alias.lower()
            if alias and alias in nouns:
                skills_count_dict[skill[0]]+=1


print(skills_count_dict)
print(len(job_list))



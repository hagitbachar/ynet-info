import requests
from bs4 import BeautifulSoup
import csv


def cleaner(line):
    clean_line = str(line).split(">")[1]
    return clean_line.split(" <")[0]


def cleaner_date(line):
    clean_line = str(line).split(">")[1]
    return clean_line.split("<")[0]


# Collect and parse first page
page = requests.get('https://www.ynet.co.il/headlines/0,7340,L-188-11301,00.html')
soup = BeautifulSoup(page.text, 'html.parser')

# Pull all text from the BodyText div
data = soup.find(id='tbl_mt')

# Pull text from all instances of <a> tag within BodyText div
title = data.find_all('a')

articles = data.find_all('font')

articles.remove(articles[0])

f = csv.writer(open('ynet.csv', 'w'))
f.writerow(['Title', 'Name', 'Date'])

i = 0
while (i < len(articles) - 2):
    f.writerow([cleaner(title[int(i / 3)]), cleaner(articles[i + 1]), cleaner_date(articles[i + 2])])
    i += 3


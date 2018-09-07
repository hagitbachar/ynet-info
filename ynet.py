import requests
from bs4 import BeautifulSoup
import csv
import datetime
import re, cgi

WEEK = 7

#clean the content of the article
def strip_html(string):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    # Remove well-formed tags, fixing mistakes by legitimate users
    no_tags = tag_re.sub('', string)

    # Clean up anything else by escaping
    return cgi.escape(no_tags)

#convert the data to a datatime object
def convert_date(ynet_date):
    year = int("20"+ynet_date[-4:-2])
    month = int(ynet_date[-7:-5])
    hour = int(ynet_date[1:3])
    minute = int(ynet_date[4:6])
    day = int(ynet_date[9:11])
    return datetime.datetime(year, month, day, hour, minute)


def cleaner(line):
    clean_line = str(line).split(">")[1]
    return clean_line.split(" <")[0]


def cleaner_date(line):
    clean_line = str(line).split(">")[1]
    return clean_line.split("<")[0]


def cleaner_title(line):
    href = str(line).split('href="')[1]
    link = href.split('">')[0]
    topic = href.split('">')[1]
    topic = topic.split(" <")[0]
    return topic, link

#extract the content of the article and the links for the images
def get_article_info(link):
    link = link.replace('/articles/0,7340',
            'https://www.ynet.co.il/Ext/Comp/ArticleLayout/CdaArticlePrintPreview/0,2506') # Convert to print version

    child_page = requests.get(link)
    child_data = child_page.text.split("<font STYLE='font-size:12px; font-weight:normal; color:#000000;'> ")[1]
    child_data = child_data.split("</font><br>")[0]
    child_soup = BeautifulSoup(child_data, 'html.parser')
    child_body = child_soup.find_all("p")
    img = child_soup.find_all(class_="text12")

    output = list()
    for line in child_body:
        line = str(line).replace('\xa0', '')
        output.append(strip_html(str(line)))

    list_img = list()
    for image in img:
        url = str(image).split('src="')[1].split('"')[0]
        list_img.append(url)

    return output, list_img



# Collect and parse first page
page = requests.get('https://www.ynet.co.il/headlines/0,7340,L-188-11301,00.html')
soup = BeautifulSoup(page.text, 'html.parser')

# Pull all text from the BodyText div
data = soup.find(id='tbl_mt')

# Pull text from all instances of <a> tag within BodyText div
title = data.find_all('a')

articles = data.find_all('font')

articles.remove(articles[0])

f = csv.writer(open('ynet_update.csv', 'w'))
f.writerow(['Title', 'link', 'Name', 'Date', 'content', 'images'])

i = 0
while (i < len(articles) - 2):
    title_info = cleaner_title(title[int(i / 3)])
    article_date = cleaner_date(articles[i + 2])
    #take informarion from the articles from the last week
    if (datetime.datetime.now() - convert_date(article_date)) <= datetime.timedelta(days=WEEK):
        article_info = get_article_info(title_info[1])
        body = article_info[0]
        images = article_info[1:]
        f.writerow([title_info[0], title_info[1], cleaner(articles[i + 1]), article_date, body, images])

    i += 3

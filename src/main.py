import datetime
import json
import random
import smtplib
import subprocess
import time
import urllib
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dominate
import requests
import yaml
from dominate.tags import *


def get_random_items(config, n=5):

    params = {
        'consumer_key' : config['consumer_key'],
        'access_token': config['access_token'],
        'state': 'unread',
    }
    headers = {
        'Content-Type' : 'application/json; charset=UTF8',
        'X-Accept' : 'application/json'
    }
    resp = requests.post("https://getpocket.com/v3/get", json=params, headers=headers)

    if str(resp.status_code)[0] == '4':
        raise Exception("access_code_expired")

    articles = resp.json()['list']
    reading_list = [articles[random.choice(list(articles.keys()))] for i in range(n)]

    return reading_list


def gen_email_content(reading_list, word_count = True):

    doc = dominate.document(title='Reading list')

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        today = datetime.date.today()
        h1("Reading list for %d/%d/%d" % (today.day, today.month, today.year))
        with div(id='body').add(ul()):
            for e in reading_list:
                li(a(e['given_title'], href="https://getpocket.com/read/" + e['item_id']), f', {e["word_count"]} words')

    return doc



if __name__ == '__main__':
    with open("config.yml", "r") as configf:
        config = yaml.safe_load(configf)
    fromaddr = config['from_addr']
    toaddrs  = config['to_addr']

    message = MIMEMultipart("alternative")
    message["From"] = "Cpt-n3m0"
    message["To"] = "Cpt-n3m0"
    today = datetime.date.today()
    message["Subject"] = 'Reading List (%d/%d/%d)' % (today.day, today.month, today.year)

    try:
        reading_list = get_random_items(config)
        email_html = str(gen_email_content(reading_list))
    except Exception as err:
        if str(err) == "access_code_expired":
            email_html = "<h1> Pocketmail's access token expired <\h1>"
        else:
            email_html = "<h1> Unknown error has occured you fucked something up in the script <\h1>"
    content = MIMEText(email_html, "html")
    message.attach(content)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(config['email_user'], config['email_pass'])


    server.sendmail(fromaddr, toaddrs,message.as_string())
    server.quit()

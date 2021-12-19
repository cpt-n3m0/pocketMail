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
from watchdog.events import FileSystemEventHandler, LoggingEventHandler
from watchdog.observers import Observer

with open("config.yml", "r") as configf:
    config = yaml.safe_load(configf)


access_token = None



def block_until_changed(path):

    class isModified(FileSystemEventHandler):
        def __init__(self):
            super()
            self.modified = False

        def on_modified(self, event):
            self.modified = True

    event_handler = isModified()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    while not event_handler.modified:
        time.sleep(0.5)
    observer.stop()
    observer.join()

    return

def auth():
    req_params = {
        'consumer_key' : config['consumer_key'],
        'redirect_uri' : config['callback_uri']
    }
    header = {
        'Content-Type' : 'application/json; charset=UTF8',
        'X-Accept' : 'application/json'
    }

    resp = requests.post("https://getpocket.com/v3/oauth/request", json=req_params, headers=header)
    req_token = resp.json()['code']
    auth_params = {
        'consumer_key' : config['consumer_key'],
        'code' : req_token
    }
    webbrowser.open(f'https://getpocket.com/auth/authorize?request_token={req_token}&redirect_uri={urllib.parse.quote(config["callback_uri"])}')
    block_until_changed('status')
    resp = requests.post("https://getpocket.com/v3/oauth/authorize", json=auth_params, headers=header)

    return resp.json()['access_token']

def get_random_items(n=5):
    global access_token

    if access_token is None:
        access_token = auth()
    params = {
        'consumer_key' : config['consumer_key'],
        'access_token': access_token,
        'state': 'unread',
    }
    headers = {
        'Content-Type' : 'application/json; charset=UTF8',
        'X-Accept' : 'application/json'
    }
    resp = requests.post("https://getpocket.com/v3/get", json=params, headers=headers)

    if not resp.ok:
        # access token expired
        access_token = auth()
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
                li(a(e['given_title'], href=e['given_url']), f', {e["word_count"]} words')

    return doc



if __name__ == '__main__':
    reading_list = get_random_items()
    fromaddr = config['from_addr']
    toaddrs  = config['to_addr']

    message = MIMEMultipart("alternative")
    message["From"] = "Cpt-n3m0"
    message["To"] = "Cpt-n3m0"
    today = datetime.date.today()
    message["Subject"] = 'Reading List (%d/%d/%d)' % (today.day, today.month, today.year)

    email_html = str(gen_email_content(reading_list))
    content = MIMEText(email_html, "html")
    message.attach(content)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(config['email_user'], config['email_pass'])


    server.sendmail(fromaddr, toaddrs,message.as_string())
    server.quit()

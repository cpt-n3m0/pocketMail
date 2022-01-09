import datetime
import os
import random
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dominate
import requests
import yaml
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from dominate.tags import *

CONFIG_PATH="../config.yml"

def index(request):
    global access_token, request_token

    print(os.getcwd())
    with open(CONFIG_PATH , "r") as configf:
        config = yaml.safe_load(configf)

    print("Got request, initiating auth procedure")

    req_params = {
        'consumer_key' : config['consumer_key'],
        'redirect_uri' : config['callback_uri']
    }
    header = {
        'Content-Type' : 'application/json; charset=UTF8',
        'X-Accept' : 'application/json'
    }

    print("Fetching request token...")
    resp = requests.post("https://getpocket.com/v3/oauth/request", json=req_params, headers=header)
    request_token = resp.json()['code']
    print("Request token received, redirecting...", str(request_token))

    callback_uri = urllib.parse.quote(config["callback_uri"])

    return redirect(f'https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={callback_uri}')


def authenticated(request):
    global access_token, request_token

    with open(CONFIG_PATH, "r") as configf:
        config = yaml.safe_load(configf)
    print("handling callback and getting auth code")
    req_params = {
            'consumer_key' : config['consumer_key'],
            'code' : request_token
    }
    header = {
        'Content-Type' : 'application/json; charset=UTF8',
        'X-Accept' : 'application/json'
    }

    resp = requests.post("https://getpocket.com/v3/oauth/authorize", json=req_params, headers=header)
    access_token = resp.json()['access_token']
    config['access_token'] = access_token

    with open(CONFIG_PATH, "w") as configf:
        configf.write(yaml.dump(config))
        print("Written", access_token)


    return HttpResponse("Success! access token saved")

# def get_random_items(config, n=5):
    # global access_token


    # params = {
        # 'consumer_key' : config['consumer_key'],
        # 'access_token': access_token,
        # 'state': 'unread',
    # }
    # headers = {
        # 'Content-Type' : 'application/json; charset=UTF8',
        # 'X-Accept' : 'application/json'
    # }
    # resp = requests.post("https://getpocket.com/v3/get", json=params, headers=headers)

    # if not resp.ok:
        # raise Exception()
    # articles = resp.json()['list']
    # reading_list = [articles[random.choice(list(articles.keys()))] for i in range(n)]

    # return reading_list


# def gen_email_content(reading_list, word_count = True):

    # doc = dominate.document(title='Reading list')

    # with doc.head:
        # link(rel='stylesheet', href='style.css')

    # with doc:
        # today = datetime.date.today()
        # h1("Reading list for %d/%d/%d" % (today.day, today.month, today.year))
        # with div(id='body').add(ul()):
            # for e in reading_list:
                # # li(a(e['given_title'], href=e['given_url']), f', {e["word_count"]} words')
                # li(a(e['given_title'], href="https://getpocket.com/read/" + e['item_id']), f', {e["word_count"]} words')

    # return doc



# def email_readinglist(config):
    # reading_list = get_random_items(config)
    # fromaddr = config['from_addr']
    # toaddrs  = config['to_addr']

    # message = MIMEMultipart("alternative")
    # message["From"] = "Cpt-n3m0"
    # message["To"] = "Cpt-n3m0"
    # today = datetime.date.today()
    # message["Subject"] = 'Reading List (%d/%d/%d)' % (today.day, today.month, today.year)

    # email_html = str(gen_email_content(reading_list))
    # content = MIMEText(email_html, "html")
    # message.attach(content)
    # server = smtplib.SMTP('smtp.gmail.com:587')
    # server.ehlo()
    # server.starttls()
    # server.login(config['email_user'], config['email_pass'])


 

#!/usr/bin/env python3

import time
import json
import datetime
import os
from getpass import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
from selenium import webdriver
from xvfbwrapper import Xvfb



def send_mail(to, subject, text, attach):
    msg = MIMEMultipart()

    msg['From'] = gmail_user

    if(type(to) is list):
       msg['To'] = " ,".join(to)
    else:
       msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    #part = MIMEBase('application', 'octet-stream')
    #part.set_payload(open(attach, 'rb').read())
    #Encoders.encode_base64(part)
    #part.add_header('Content-Disposition',
    #        'attachment; filename="%s"' % os.path.basename(attach))
    #msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

with open('config.json') as config:
    cfg = json.load(config)
    gmail_user = cfg['gmail_username']
    mail_to = cfg['mail_to']
    njuskalo = cfg['njuskalo']
    index = cfg['index']
    oglasnik = cfg['oglasnik']

print("Enter password for gmail account {}:".format(gmail_user))
gmail_pwd = getpass()

xpath_njuskalo = '//*[@id="form_browse_detailed_search"]/div/div[1]/div[3]/div[4]/ul//article//h3/a'
xpath_index = "//div[@class='results']//a[@class='result']"
xpath_oglasnik = '//div[@id="ads-list"]//a'

os.system('clear')
print("Initializing..")

display = Xvfb()
display.start()
driver = webdriver.Chrome()

if njuskalo:
    driver.get(njuskalo)
    elem = driver.find_elements_by_xpath(xpath_njuskalo)
    links_njuskalo = [e.get_attribute("href") for e in elem]
    print("Got njuskalo..")

if index:
    driver.get(index)
    elem = driver.find_elements_by_xpath(xpath_index)
    links_index = [e.get_attribute("href") for e in elem]
    print("Got index..")

if oglasnik:
    driver.get(oglasnik)
    elem = driver.find_elements_by_xpath(xpath_oglasnik)
    links_oglasnik = [e.get_attribute("href") for e in elem]
    print("Got oglasnik..")

print("Initialized!")
send_mail(mail_to, "Autostan successfully started.", "", None)

counter = 0
try:
    while True:
        mail_body = ""
        temp_index = []
        temp_njuskalo = []
        temp_oglasnik = []

        #os.system('clear')
        print(str(datetime.datetime.now()))

        ####### NJUSKALO
        if njuskalo:
            try:
                driver.get(njuskalo)
                elem = driver.find_elements_by_xpath(xpath_njuskalo)
                temp_njuskalo = [e.get_attribute("href") for e in elem]
                print("Got njuskalo..", end="\r")
            except KeyboardInterrupt:
                driver.quit()
                display.stop()
            except:
                print("Skipping njuskalo!")
                pass

        ####### INDEX
        if index:
            try:
                driver.get(index)
                elem = driver.find_elements_by_xpath(xpath_index)
                temp_index = [e.get_attribute("href") for e in elem]
                print("Got index..", end="\r")
            except KeyboardInterrupt:
                driver.quit()
                display.stop()
            except:
                print("Skipping index!")
                pass

        ####### OGLASNIK
        if oglasnik:
            try:
                driver.get(oglasnik)
                elem = driver.find_elements_by_xpath(xpath_oglasnik)
                temp_oglasnik = [e.get_attribute("href") for e in elem]
                print("Got oglasnik..", end="\r")
            except KeyboardInterrupt:
                driver.quit()
                display.stop()
            except:
                print("Skipping oglasnik!")
                pass

        for t in temp_index+temp_njuskalo+temp_oglasnik:
            if t not in links_index+links_njuskalo+links_oglasnik:
                mail_body = mail_body + t + "\n"

        if mail_body != "":
            #print("###############################")
            print("New entries found! Notifying..")
            print(mail_body)

            if len(temp_oglasnik) > 0:
                links_oglasnik = temp_oglasnik

            if len(temp_index) > 0:
                links_index = temp_index

            if len(temp_njuskalo) > 0:
                links_njuskalo = temp_njuskalo

            counter += 1
            mail_title = "Novi stanovi - " + str(counter)

            try:
                send_mail(mail_to, mail_title, mail_body, None)
            except Exception as e:
                print(e + "\n" + mail_body)
                send_mail(mail_to, "Autostan error", e + "\n" + mail_body, None)
                continue

        else:
            print("No new values found.")

        print()
        print("Sleeping...", end="\r")
        time.sleep(5*60)

except KeyboardInterrupt:
    driver.quit()
    display.stop()
driver.quit()
display.stop()

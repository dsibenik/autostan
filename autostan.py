#!/usr/bin/env python3

from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from xvfbwrapper import Xvfb
from getpass import getpass
import time
import datetime
import os


def send_mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
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


print("Enter gmail account:")
gmail_user = input()
print("Enter passwod:")
gmail_pwd = getpass()
send_mail("dsibenik@live.com", "autostan started", "", None)

njuskalo = "http://www.njuskalo.hr/iznajmljivanje-stanova?locationId=1153&price%5Bmin%5D=220&price%5Bmax%5D=405&mainArea%5Bmin%5D=29&mainArea%5Bmax%5D=65"

display = Xvfb()
display.start()
driver = webdriver.Chrome()
driver.get(njuskalo)

#elem = driver.find_elements_by_xpath("//ul[@class='EntityList-items']//article//h3[@class='entity-title']/a")
elem = driver.find_elements_by_xpath('//*[@id="form_browse_detailed_search"]/div/div[1]/div[3]/div[4]/ul//article//h3/a')

links_njus = [e.get_attribute("href") for e in elem]

counter = 0
try:
    while True:
        mail_body = ""
        driver.get(njuskalo)
        elem = driver.find_elements_by_xpath('//*[@id="form_browse_detailed_search"]/div/div[1]/div[3]/div[4]/ul//article//h3/a')
        temp = [e.get_attribute("href") for e in elem]

        os.system('clear')
        print(str(datetime.datetime.now()))
        for t in temp:
            print(t)
            if t not in links_njus:
                mail_body = mail_body + t + "\n"
        if mail_body != "":
            print("###############################")
            print("New entries found! Notifying..")
            print(mail_body)
            links_njus = temp
            counter += 1
            mail_title = "Novi stanovi - njuskalo - " + str(counter)
            send_mail("dsibenik@live.com", mail_title, mail_body, None)
            send_mail("m.zanetic@hotmail.com", mail_title, mail_body, None)
            send_mail("mzanetic@erstebank.com", mail_title, mail_body, None)
        time.sleep(30)
except KeyboardInterrupt:
    driver.quit()
    display.stop()
driver.quit()
display.stop()

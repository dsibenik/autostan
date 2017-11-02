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
gmail_pwd = getpass()
send_mail("dsibenik@live.com", "autostan started", "", None)

njuskalo = "http://www.njuskalo.hr/iznajmljivanje-stanova?locationId=1153&price%5Bmin%5D=220&price%5Bmax%5D=405&mainArea%5Bmin%5D=29&mainArea%5Bmax%5D=65"
index = "http://www.index.hr/oglasi/najam-stanova/gid/3279?pojam=&sortby=1&elementsNum=10&cijenaod=220&cijenado=405&tipoglasa=1&pojamZup=1153&grad=&naselje=&attr_Int_988=30&attr_Int_887=65&attr_bit_stan=&attr_bit_brojEtaza=&attr_gr_93_1=&attr_gr_93_2=&attr_Int_978=&attr_Int_1334=&attr_bit_prodavac=&attr_bit_eneregetskiCertifikat=&vezani_na=988-887_562-563_978-1334"
oglasnik = "http://www.oglasnik.hr/stanovi-najam?ad_location_2%5B%5D=7442&ad_price_from=1.500&ad_price_to=3.010&ad_params_44_from=28&ad_params_44_to=65"

xpath_njuskalo = '//*[@id="form_browse_detailed_search"]/div/div[1]/div[3]/div[4]/ul//article//h3/a'
xpath_index = "//div[@class='results']//a[@class='result']"
xpath_oglasnik = '//div[@id="ads-list"]//a'

print("Initializing..")

display = Xvfb()
display.start()
driver = webdriver.Chrome()

driver.get(njuskalo)
elem = driver.find_elements_by_xpath(xpath_njuskalo)
links = [e.get_attribute("href") for e in elem]
print("Got njuskalo..")

driver.get(index)
elem = driver.find_elements_by_xpath(xpath_index)
links = links + [e.get_attribute("href") for e in elem]
print("Got index..")

driver.get(oglasnik)
elem = driver.find_elements_by_xpath(xpath_oglasnik)
links = links + [e.get_attribute("href") for e in elem]
print("Got oglasnik..")

print("Initialized!")

counter = 0
try:
    while True:
        mail_body = ""
        temp = []

        os.system('clear')
        print(str(datetime.datetime.now()))

        ####### NJUSKALO
        try:
            driver.get(njuskalo)
            elem = driver.find_elements_by_xpath(xpath_njuskalo)
            temp = temp + [e.get_attribute("href") for e in elem]
            print("Got njuskalo..")
        except KeyboardInterrupt:
            driver.quit()
            display.stop()
        except:
            print("Skipping njuskalo!")
            pass

        ########## INDEX
        try:
            driver.get(index)
            elem = driver.find_elements_by_xpath(xpath_index)
            temp = temp + [e.get_attribute("href") for e in elem]
            print("Got index..")
        except KeyboardInterrupt:
            driver.quit()
            display.stop()
        except:
            print("Skipping index!")
            pass

        ########## OGLASNIK
        try:
            driver.get(oglasnik)
            elem = driver.find_elements_by_xpath(xpath_oglasnik)
            temp = temp + [e.get_attribute("href") for e in elem]
            print("Got oglasnik..")
        except KeyboardInterrupt:
            driver.quit()
            display.stop()
        except:
            print("Skipping oglasnik!")
            pass

        print()
        for t in temp:
            print(t)
            if t not in links:
                mail_body = mail_body + t + "\n"

        if mail_body != "":
            print("###############################")
            print("New entries found! Notifying..")
            print(mail_body)
            links = temp
            counter += 1
            mail_title = "Novi stanovi - " + str(counter)
            send_mail("dsibenik@live.com", mail_title, mail_body, None)
            send_mail("m.zanetic@hotmail.com", mail_title, mail_body, None)
            send_mail("mzanetic@erstebank.com", mail_title, mail_body, None)

        time.sleep(30)

except KeyboardInterrupt:
    driver.quit()
    display.stop()
driver.quit()
display.stop()

#!/usr/bin/env python3

import time
import json
import datetime
import os
import pickle
import sys
from getpass import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

import sqlite3
from sqlite3 import Error
from bs4 import BeautifulSoup
from selenium import webdriver
from xvfbwrapper import Xvfb


class sqldb:
    conn = None
    cursor = None

    def create_connection(self, path_to_db):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(path_to_db)
            self.cursor = self.conn.cursor()
            print(sqlite3.version)

        except Error as e:
            print(e)


    def create_table(self, table_name):
        if self.conn is not None:
            sql_ct_code = """CREATE TABLE {}
                                (   [id] INTEGER PRIMARY KEY,
                                    [date] numeric,
                                    [site] text,
                                    [link] text
                                ); """.format(table_name)   
            self.cursor.execute(sql_ct_code)
            self.conn.commit()

        else:
            print('No connection to db.') 


    def insert_row(self, table, data):
        if self.conn is not None:

            try:
                sql_code = """INSERT INTO {} VALUES (""".format(table) + (len(data)-1)*"?," + "?);"

                self.cursor.execute(sql_code, data)
                self.conn.commit()

                return self.cursor.rowcount

            except Error as e:
                print("database.py:", e)

        else:
            print('No connection to db.') 



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



def get_links(driver, link, xpath):
    temp_links = []

    try:
        driver.get(link)
        elem = driver.find_elements_by_xpath(xpath)
        temp_links = [e.get_attribute("href") for e in elem]
        print("Got from {}".format(link))
    except KeyboardInterrupt:
        driver.quit()
        display.stop()
    except:
        print(sys.exc_info()[0])
        print("Skipping {}!".format(link))
        pass

    return temp_links


def contains(start_string, string_list):
    for string in string_list:
        if string in start_string:
            return 1
    return 0


def check_if_new(links, site, database):
    new_links = []

    for link in links:
        database.cursor.execute('SELECT EXISTS(SELECT 1 FROM stanovi WHERE site="{}" AND link="{}")'.format(site, link));
        database.conn.commit()

        if ((not database.cursor.fetchone()[0]) and (not contains(keyword_filters, link))):
            new_links = new_links + [link]

    return new_links



if __name__ == '__main__':
    database = sqldb()
    database.create_connection("./data/stanovi.db")
    # database.create_table("stanovi")

    with open('./config.json') as config:
        cfg = json.load(config)
        gmail_user = cfg['gmail_username']
        mail_to = cfg['mail_to']
        njuskalo = cfg['njuskalo']
        index = cfg['index']
        oglasnik = cfg['oglasnik']
        keyword_filters = cfg['keyword_filters']

    print("Enter password for gmail account \"{}\":".format(gmail_user))
    gmail_pwd = getpass()

    xpath_njuskalo = "//li[contains(@class, 'EntityList-item') and contains(@class, 'EntityList-item--Regular')]//h3[contains(@class, 'entity-title')]/a"
    xpath_index = "//div[@class='results']//a[@class='result']"
    xpath_oglasnik = '//div[@id="ads-list"]//a'

    os.system('clear')
    print("Initializing..")

    display = Xvfb()
    display.start()
    driver = webdriver.Chrome()

    print("Initialized!")
    print()
    send_mail(mail_to, "Autostan successfully started.", "", None)
    
    time.sleep(5*60)
    counter = 0
    try:
        while True:
            date = datetime.datetime.now().strftime("%d.%m.%Y")
            mail_body = ""
            temp_njuskalo = []
            temp_index = []
            temp_oglasnik = []
            new_listings = []

            os.system('clear')
            print(str(datetime.datetime.now()))

            
            ####### NJUSKALO
            if njuskalo:
                temp_njuskalo = get_links(driver, njuskalo, xpath_njuskalo)
                temp_njuskalo = check_if_new(temp_njuskalo, "njuskalo", database)
                for listing in temp_njuskalo:
                    database.insert_row("stanovi(date, site, link)", (date, "njuskalo", listing) )
                new_listings = new_listings + temp_njuskalo

            ####### INDEX
            if index:
                temp_index = get_links(driver, index, xpath_index)
                temp_index = check_if_new(temp_index, "index", database)
                for listing in temp_index:
                    database.insert_row("stanovi(date, site, link)", (date, "index", listing) )
                new_listings = new_listings + temp_index

            ####### OGLASNIK
            if oglasnik:
                temp_oglasnik = get_links(driver, oglasnik, xpath_oglasnik)
                temp_oglasnik = check_if_new(temp_index, "oglasnik", database)
                for listing in temp_oglasnik:
                    database.insert_row("stanovi(date, site, link)", (date, "oglasnik", listing) )
                new_listings = new_listings + temp_oglasnik

            for t in new_listings:
                mail_body = mail_body + t + "\n"

            if mail_body != "":
                print("New entries found! Notifying..")
                print(mail_body)

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
            time.sleep(30*60)

    except KeyboardInterrupt:
        driver.quit()
        display.stop()
    driver.quit()
    display.stop()

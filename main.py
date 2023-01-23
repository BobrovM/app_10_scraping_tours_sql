import time
import requests
import selectorlib
import smtplib, ssl, os
import psycopg2 as pg


URL = "http://programmer100.pythonanywhere.com/tours/"

def scrape(link):
    response = requests.get(link)
    text = response.text
    return text


def extract(text):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(text)["tours"]
    return value


def send_email(extracted):
    host = "smtp.gmail.com"
    port = 465 # due to ssl

    mail = "officeguyyt@gmail.com"
    password = os.environ["SMTP_PASSWORD"]
    context = ssl.create_default_context()

    message = f"""\
Subject: New tour!

Message: {extracted}
"""
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(mail, password)
        server.sendmail(mail, mail, message)

    print("Email was sent!")


def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    connection = pg.connect("dbname=pc_d10_tours_events user=postgres password=4531")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(%s,%s,%s)", row)
    connection.commit()
    cursor.close()
    connection.close()


def read_db(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, tdate = row
    connection = pg.connect("dbname=pc_d10_tours_events user=postgres password=4531")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=%s AND city=%s AND tdate=%s", (band, city, tdate))
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return row


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            content = read_db(extracted)
            if not content:
                store(extracted)
                send_email(extracted)
        time.sleep(15)

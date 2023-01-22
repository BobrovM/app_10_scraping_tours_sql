import time
import requests
import selectorlib
import smtplib, ssl, os


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
    with open("data.txt", "a") as file:
        file.write(extracted + "\n")


def read_file():
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            content = read_file()
            if extracted not in content:
                store(extracted)
                send_email(extracted)
        time.sleep(15)

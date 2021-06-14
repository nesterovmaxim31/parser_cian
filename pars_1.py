import requests
import re
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

Number = 0
FILE = "cian7.csv"
name = []
URL = "https://www.cian.ru/cat.php?currency=2&deal_type=rent&engine_version=2&maxprice=65000&metro%5B0%5D=133&offer_type=flat&room1=1&room2=1&room3=1&type=4"
Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
Chablon = re.compile(r"[\d а-яёА-ЯЁ0-9-:./]*")


#  /м²₽

def get_html(url, param=None):
    req = requests.get(url, params=param, headers=Headers)
    return req


def sum_list(list):
    F = ''
    for g in list:
        F += g
    return F


def number_of_page(html):
    soup = BeautifulSoup(html.text, "html.parser")
    divi = soup.find_all("a", class_="_93444fe79c--list-itemLink--3o7_6")
    if divi:
        return int(divi[-1].get_text())
    else:
        return 1


def link_to_second_page(html):
    soup = BeautifulSoup(html.text, "html.parser")
    divi = soup.find("a", class_="_93444fe79c--list-itemLink--3o7_6").get("href")
    return divi


def ifi(N):
    if N:
        return N.get_text()
    else:
        return "Не указан"


def seconde_variante(URL):
    driver = webdriver.Chrome()
    driver.get(URL)
    b = input()
    main_page = driver.page_source
    return main_page


def get_content(html):
    global Number
    soup = BeautifulSoup(html, "html.parser")
    if soup.find("title").get_text() == "Captcha - база объявлений ЦИАН":
        print("пипец")
        return False
    divi = soup.find_all("article", {"data-name": "CardComponent"})
    for u in divi:
        name.append({
            'title': sum_list(Chablon.findall(u.find("div", class_='_93444fe79c--container--JdWD4').get_text())),
            'link': u.find('a', class_="_93444fe79c--link--39cNw").get("href"),
            'metro': ifi(u.find("a", class_='_93444fe79c--link--3ruIo')),
            'time to metro': ifi(u.find("div", class_='_93444fe79c--remoteness--1BnAC')),
            'address': u.find("div", class_="_93444fe79c--labels--1J6M3").get_text(),
            'builder': ifi(u.find('a', class_='_93444fe79c--jk--YYtNL')),
            'price to m2': sum_list(Chablon.findall(u.find("p", {"data-mark": "PriceInfo"}).get_text())),
            'price': sum_list(Chablon.findall(u.find("span", {"data-mark": "MainPrice"}).get_text()))
        })
        Number += 1
    # print(name)
    # print(len(name))

    return name


def save_file(divi, path):
    with open(path, "w", newline="") as file:
        wr = csv.writer(file, delimiter=";")
        wr.writerow(
            ["Название", "Ссылка", "Метро", "Время до метро", "Адрес", "Застройщик", "Цена за квадратный метр в рублях",
             "Цена в рублях"])
        for item in divi:
            wr.writerow([item['title'], item['link'], item['metro'], item["time to metro"], item["address"],
                         item["builder"], item['price to m2'], item['price']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        if not get_content(html.text):
            print("Captcha fuuuk")
            pass
        else:
            save_file(get_content(html.text), FILE)
            N = number_of_page(html)
            print("Завершено 1 из {}".format(N))
            if N == 2:
                Link = link_to_second_page(html)
                print(Link)
                html = get_html(Link)
                save_file(get_content(html), FILE)
            elif N > 2:
                Link = link_to_second_page(html)
                for i in range(2, N + 1):
                    if i > 2:
                        html = get_html(Link, param={"p": i})
                    else:
                        html = get_html(Link)
                    print(html.url)
                    save_file(get_content(html.text), FILE)
                    print("Завершено {} из {}".format(i, N))
    else:
        print("Возникла ошибка при работе, убедитесь в правильности ссылки")


if __name__ == "__main__":
    parse()
print(Number)
# https://www.cian.ru/kupit-3-komnatnuyu-kvartiru-novostroyki-moskva-stanciya-mck-botanicheskiy-sad/
# https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&metro%5B0%5D=21&object_type%5B0%5D=2&offer_type=flat&p=2&room3=1

import re
import requests
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from multiprocessing import Pool
import csv

Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
LINK = "https://freelance.habr.com/tasks?_=1623421844355&page=1&q=python"
Htmls = []
Htmls.append(LINK)
names = []
chrome_options = Options()
chrome_options.add_argument("--headless")

reg = re.compile('[a-zA-Z 0-9а-яёА-ЯЁ]')


# 9:10
#

def sum_list(list):
    F = ''
    for g in list:
        F += g
    return F


def number_of_pages(soup):
    if soup.find('div', class_="pagination"):
        divi = soup.find('div', class_="pagination").find_all('a')
        return int(divi[-2].get_text())
    else:
        return 1


def ifi_2(N):
    if N:
        return N.find('i', class_='params__count').get_text()
    else:
        return 'Не указан'


def get_html(link):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    html = driver.page_source
    # r = requests.get(link)
    return html


def get_price(link):
    Html = get_html(link)
    soup = BeautifulSoup(Html, "html.parser")
    return reg.sub('', soup.find('div', class_='task__finance').get_text())


def save_sqlite(string):
    con = sqlite3.connect("Fas.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO cooling2(telegram) VALUES('{string}')")
    con.commit()
    con.close()


def divi_parse(Link):
    Html = get_html(Link)
    soup = BeautifulSoup(Html, "html.parser")
    divi = soup.find_all('li', class_='content-list__item')
    for t in divi:
        N = 'https://freelance.habr.com' + t.find('div', class_='task__title').find('a').get('href')
        D = {
            'Title': t.find('div', class_='task__title').get_text(),
            'Link': N,
            'Price': get_price(N),
            "Number_of_otkliks": ifi_2(t.find('span', class_='params__responses icon_task_responses')),
            'Number_of_vues': ifi_2(t.find('span', class_="params__views icon_task_views"))
        }
        save_sqlite(f"{sum_list(reg.findall(D['Title']))}")


def parse():
    Html = get_html(LINK)
    soup = BeautifulSoup(Html, "html.parser")
    Ni = number_of_pages(soup)
    if Ni > 1:
        for i in range(2, Ni + 1):
            LINK_2 = LINK.replace(f'&page=1', f'&page={i}')
            Htmls.append(LINK_2)
    p = Pool(16)
    p.map(divi_parse, Htmls)


if __name__ == "__main__":
    parse()

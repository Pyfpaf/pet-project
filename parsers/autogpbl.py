import requests
import json
import csv
import os
from bs4 import BeautifulSoup

url = 'https://auction.autogpbl.ru/auction?page='

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
}


def get_data():
    # s = requests.Session()
    # resp = s.get(url=url, headers=headers)
    #
    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(resp.text)

    with open('data/index.html', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    cards = soup.find_all('article', class_='css-zt7hdf')

    for card in cards:

        full_item = (
            card.find('div', class_='css-u8gsze').find('div', class_='typography default css-1m5714k').text.strip())

        fail_word = ['рицеп', 'ватор', 'грузчик', 'станов', 'реза', 'аток', 'кран', 'Кран', 'асси',
                     'втобус', 'еларус', 'ашинострои', 'усоровоз', 'дозер', 'тилифт', 'рактор',
                     'омбайн', 'рейдер', 'уидор', 'орвардер']

        if any(word in full_item for word in fail_word):
            continue

        factory = full_item.replace(',', '').split()[0].lower()
        model = (full_item.replace(',', '').replace('(Shaanxi)', '').replace('(Lada) ', '').replace('*', '').split()[
                     1].lower())
        year = int(full_item.split()[-1])
        city = \
        card.find('div', class_='css-u8gsze').find('div', class_='typography default css-uukhpx').text.strip().split()[
            0].lower()
        price = int(
            card.find('div', class_='css-u8gsze').find('div', class_='primary-text css-1ctn9oc').text.strip().replace(
                ' ', '').replace('₽', ''))

        try:
            mileage_full = \
            card.find('div', class_='css-u8gsze').find_all('div', class_='typography default css-bdji1y')[0].text

            if 'км' in mileage_full:
                mileage = mileage_full.strip().replace(' ', '').replace(' км', '')
            else:
                mileage = None

        except:
            mileage = None

        print(f'{factory} ## {model} ## {year} ## {city} ## {mileage} ## {price}')


def get_page():
    s = requests.Session()

    for i in [39, 40]:
        resp = s.get(url=url + str(i), headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        cards = soup.find_all('article', class_='css-zt7hdf')

        try:
            print(cards[0].find('div', class_='css-u8gsze').find('div', class_='typography default css-1m5714k').text.strip())
        except:
            print(f'страница {i} отсутствует на сайте')


def main():
    get_page()


if __name__ == '__main__':
    main()

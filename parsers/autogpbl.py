import requests
import json
import csv
import os
import logging
import time
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


url = 'https://auction.autogpbl.ru/auction?page='

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
}

path = os.environ.get('PROJECT_PATH', '.')
cards_item = []


def get_data():

    s = requests.Session()

    page = 1

    while True:
        resp = s.get(url=url + str(page), headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        cards = soup.find_all('article', class_='css-zt7hdf')

        if cards:

            for card in cards:

                full_item = (card.find('div', class_='css-u8gsze').find('div', class_='typography default css-1m5714k').text.strip())

                fail_word = ['рицеп', 'ватор', 'грузчик', 'станов', 'реза', 'аток', 'кран', 'Кран', 'асси',
                             'втобус', 'еларус', 'ашинострои', 'усоровоз', 'дозер', 'тилифт', 'рактор',
                             'омбайн', 'рейдер', 'уидор', 'орвардер']

                if any(word in full_item for word in fail_word):
                    continue

                factory = full_item.replace(',', '').split()[0].lower()
                model = (full_item.replace(',', '').replace('(Shaanxi)', '').replace('(Lada) ', '').replace('*', '').split()[1].lower())

                try:
                    year = int(full_item.split()[-1])
                except:
                    year = None

                try:
                    city = card.find('div', class_='css-u8gsze').find('div', class_='typography default css-uukhpx').text.strip().split()[0].lower()
                except:
                    city = None

                try:
                    price = int(card.find('div', class_='css-u8gsze').find('div', class_='primary-text css-1ctn9oc').text.strip().replace(' ', '').replace('₽', ''))
                except:
                    price = None

                try:
                    mileage_full = \
                    card.find('div', class_='css-u8gsze').find_all('div', class_='typography default css-bdji1y')[0].text

                    if 'км' in mileage_full:
                        mileage = mileage_full.strip().replace(' ', '').replace(' км', '')
                    else:
                        mileage = None

                except:
                    mileage = None

                cards_item.append(
                    {
                        'factory': factory,
                        'model': model,
                        'year': year,
                        'city': city,
                        'mileage': mileage,
                        'price': price
                    }
                )

            logger.info(f'[+] Обработалась страница {page}')
            time.sleep(1)

            page += 1

        else:
            logger.info(f'Страница {page - 1} была последней на сайте')
            break


def main_gpbl():

    logger.info(f'Старт работы парсинга сайта Газпром Автолизинг')
    get_data()
    with open(f'{path}/data/gpbl_data.json', 'w', encoding='utf-8') as file:
        json.dump(cards_item, file, indent=4, ensure_ascii=False)

    with open(f'{path}/data/gpbl_data.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'factory',
                'model',
                'year',
                'city',
                'mileage',
                'price'
            )
        )

    for item in cards_item:
        with open(f'{path}/data/gpbl_data.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    item['factory'],
                    item['model'],
                    item['year'],
                    item['city'],
                    item['mileage'],
                    item['price']
                )
            )
    logger.info(f'Окончание работы парсинга сайта Газпром Автолизинг')


if __name__ == '__main__':
    main_gpbl()

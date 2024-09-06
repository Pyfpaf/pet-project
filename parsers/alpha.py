import json
import csv
import logging
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


get_type = {
    'legkovye': 'Легковые',
    'gruzovye': 'Грузовые',
    'kommercheskij': 'Коммерческие',
    # 'pricepy': 'Прицепы',
    # 'spectech': 'Спецтехника',
    # 'oborudovanie': 'Оборудование'

}
url = f'https://alfaleasing.ru/rasprodazha-avto-s-probegom/'

headers = {
        'Accept': 'text / html, application / xhtml + xml, application / xml; q = 0.9, image / avif, image / webp, * / *;q = 0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
    }

path = os.environ.get('PROJECT_PATH', '')
cards_item = []


async def get_page_data(session, page, i):
    page_url = f'{url}{i}/?page={page}'

    async with session.get(url=page_url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        cards = soup.find_all('div', class_='styles_cardWrapper__HTktR')

        for card in cards:

            try:
                factory = card.find('div', class_='styles_infoWrapper__07nVQ').find('h4').text.strip().lower().split()[0]
            except:
                factory = None

            try:
                model = card.find('div', class_='styles_infoWrapper__07nVQ').find('h4').text.strip().lower().split()[1]
            except:
                model = None

            try:
                year = int(card.find('div', class_='styles_infoWrapper__07nVQ').find('span', class_='styles_year__7awpq typography__secondary_e4qmo typography__primary-small_1oeg2').text.split()[0].strip())
            except:
                year = None

            try:
                city = card.find('div', class_='styles_bottomWrapper___L5lK').find('span', class_='typography__secondary_e4qmo typography__primary-small_1oeg2').text.strip().lower()
            except:
                city = None

            try:
                mileage = int(card.find('div', class_='styles_infoWrapper__07nVQ').find('span', class_='amount__component_1o74g').text.replace(' ', '').replace(' км', '').strip())
            except:
                mileage = None

            try:
                price = int(card.find('div', class_='styles_gridVertical__I_uyZ styles_priceColumn__X5BxV').find('span', class_='amount__component_1o74g').text.replace(' ', '').replace(' ₽', '').strip())
            except:
                price = None

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


async def gather_data():
    async with aiohttp.ClientSession() as session:

        for i, v in get_type.items():
            logger.info(f'Сбор данных в категории: {v}')

            response = await session.get(url=url + i, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
            pages = int(soup.find('ul', class_='pagination_list__ctVZn').find_all('li')[-2].text)
            logger.info(f'Всего страниц в данной категории: {pages}')

            tasks = []

            for page in range(1, pages + 1):

                task = asyncio.create_task(get_page_data(session, page, i))
                await asyncio.sleep(0.05)

                tasks.append(task)

            await asyncio.gather(*tasks)


def main():
    logger.info(f'Старт работы парсинга сайта Альфа Лизинг')
    asyncio.run(gather_data())
    with open(f'{path}/data/alpha_data.json', 'w', encoding='utf-8') as file:
        json.dump(cards_item, file, indent=4, ensure_ascii=False)

    with open(f'{path}/data/alpha_data.csv', 'w', encoding='utf-8', newline='') as file:
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
        with open(f'{path}/data/alpha_data.csv', 'a', encoding='utf-8', newline='') as file:
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
    logger.info(f'Окончание работы парсинга сайта Альфа Лизинг')


if __name__ == '__main__':
    main()

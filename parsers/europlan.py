import csv
import json
import requests
import os
import asyncio
import aiohttp
from datetime import datetime

cards_item = []

get_type = [
    'https://europlan.ru/api/promo/used-offers?filter={%22nds%22:true,%22vehicleSuperTypes%22:[8],%22vehicleCategories%22:[2],%22pageType%22:1,%22page%22:1,%22sort%22:5,%22order%22:true}&page=',
    'https://europlan.ru/api/promo/used-offers?filter={%22nds%22:true,%22vehicleSuperTypes%22:[9],%22vehicleCategories%22:[6],%22pageType%22:1,%22page%22:1,%22sort%22:5,%22order%22:true}&page=',
    'https://europlan.ru/api/promo/used-offers?filter={%22nds%22:true,%22vehicleSuperTypes%22:[9],%22vehicleCategories%22:[5,7],%22pageType%22:1,%22page%22:1,%22sort%22:5,%22order%22:true}&page='
]

headers = {
        'Accept': 'application / json, text / plain, * / *',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv: 129.0) Gecko / 20100101 Firefox / 129.0'
    }

path = os.environ.get('PROJECT_PATH', '.')


async def get_page_data(session, page, i):

    async with session.get(url=i + str(page), headers=headers) as response:
        response_json = await response.json()

        for item in response_json['results']:

            try:
                factory = item.get('brandName').lower()
            except:
                factory = None

            try:
                model = item.get('modelName').lower().split()[0]
            except:
                model = None

            try:
                year = item.get('year')
            except:
                year = None

            try:
                city = item.get('cityName').lower()
            except:
                city = None

            try:
                mileage = item.get('mileage')
            except:
                mileage = None

            try:
                price = item.get('advertPrice')
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
        print(f'[+] Обработалась страница {page}')


async def gather_data():

    async with aiohttp.ClientSession() as session:

        for i in get_type:
            print(f'Сбор данных в категории: {i}')

            response = await session.get(url=i + '1', headers=headers)
            data = await response.json()

            pages = data['pager']['lastPage']
            print(f'Всего страниц в данной категории: {pages}')

            tasks = []

            for page in range(1, pages + 1):
                task = asyncio.create_task(get_page_data(session, page, i))
                await asyncio.sleep(0.05)

                tasks.append(task)

            await asyncio.gather(*tasks)

def main():

    print(f'Старт работы парсинга сайта Европлан')
    asyncio.run(gather_data())
    with open(f'{path}/data/europlan_data_{datetime.now().strftime("%Y%m%d")}.json', 'w', encoding='utf-8') as file:
        json.dump(cards_item, file, indent=4, ensure_ascii=False)

    with open(f'{path}/data/europlan_data_{datetime.now().strftime("%Y%m%d")}.csv', 'w', encoding='utf-8', newline='') as file:
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
        with open(f'{path}/data/europlan_data_{datetime.now().strftime("%Y%m%d")}.csv', 'a', encoding='utf-8', newline='') as file:
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
    print(f'Окончание работы парсинга сайта Европлан')


if __name__ == '__main__':
    main()
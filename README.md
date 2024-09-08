Описание проекта

Данный проект строит модель предсказаний цены автомобиля, который ранее находился в лизинге и на текущий момент находится на реализации лизинговой компании.
Информация по продажам автомобилей собирается с сайтов Альфа Лизинга, Европлана, Газпромбанк Автолизинга.

С помощью AirFlow один раз в неделю просходит запуск парсеров с последующим построением модели предсказаний цены.

По API можно получить информацию о моделе предсказаний и предикт цены автомобиля.

_____________________________________________________________________________________________

Структура проекта

- Папка /DAGS содержит файл dag для запуска в airflow.

- Папка /DATA аккумулирует собранные с сайтов лизинговых компаний данные о продаже автомобилей в двух форматах .csv и .json. Также в этой папке имеется субдиректория /MODELS в которой содержатся сериализованные файлы моделей предсказаний цены автомобиля.

- Папка /MODULES содержит файл паплайна построения модели предсказаний цены автомобиля.

- Папка /PARSERS содержит файлы парсинга информации о продаваемых автомобилях с сайтов лизинговых компаний: Альфа Лизинга, Европлана, Газпромбанк Автолизинга.

- Папка /TEST содержит 5 файлов со словарями информации об автомобилях для передачи в теле POST запроса на локальный разворачиваемый сервер для получения предсказания цены.

- Корень проекта содержит:
  
  * Dockerfile для создания кастомного образа;
  * docker-compose.yaml для поднятия сети контейнеровнеобходимых для работы проекта;
  * 

_____________________________________________________________________________________________

Инструкция по разворачиванию проекта

1. Сделайте клон репозитория и перейдите в папку с проектом.

2. Выполните команду: 'echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env' например с помощью GIT BASH.

3. Поднимите airflow-init с помощью Docker Сompose: docker-compose up airflow-init.

4. Поднимите Docker Compose для Airflow: docker-compose up.

5. Далее зайдите в командную строку контейнеров и установите нужный для работы пайплайна пакет scikit-learn:

docker exec -it worker_id bash

pip install scikit-learn 

и 

docker exec -it scheduler_id bash 

pip install scikit-learn

Где worker_id и scheduler_id идентификационные номера данных контейнеров. Также установку библиотеки scikit-learn можно провести непосредственно из программы docker desktop перейдя в данные контейнеры (worker и scheduler), затем выбрав вкладку Exec и в коммандной строке вкладки у обоих контейнеров введя команду pip install scikit-learn.

________________________________________________________________________________________________

Парсинг данных и построение модели предсказаний.

Для запуска задания по парсингу данных и запуску пайплайна для построения модели предсказаний перейдите на веб сервер airflow: 127.0.0.1:8080. Введите логин airflow и пароль airflow. Вручную запустите DAG на исполнение.

О выполнении работы можно смотреть во вкладке log соответствующего слоя.

________________________________________________________________________________________________

Получение предиктов по цене автомобиля.

Введите в адресную строку браузера 127.0.0.1:8000/docs. Увидите информацию о путях на сервере для получения определенной информации, а также о методе направляемого HTTP-запроса.

* GET 127.0.0.1:8000/status Получение статуса сервера

* GET 127.0.0.1:8000/version Получение информации о моделе предсказаний

* POST 127.0.0.1:8000/predict Получение предсказаний.

  Для направления пост запроса необходимо добавить тело запроса в формате словаря. Это удобно сделать например в программе Postman Agent.
  В тело запроса можно вставить текст любого словаряь из папки test, либо скопировав данные из любова json файла папки data в следующем формате:

  {
    "factory": "shacman",
    "model": "sx3318dt366",
    "year": 2021.0,
    "city": "ростов-на-дону",
    "mileage": 99833.0
  }

В ответе вы получите предикт по цене автомобиля.

**Важно!!! после получения новой модели предсказаний контейнер fastapi нужно остановить и запустить заново, чтоб подтянулась последняя и самая актуальная модель предсказаний.

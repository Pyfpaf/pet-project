Описание проекта

Данный проект строит модель предсказаний цены автомобиля, который ранее находился в лизинге и на текущий момент находится на реализации лизинговой компании.
Информация по продажам автомобилей собираются с сайтов Альфа Лизинга, Европлана, Газпромбанк Автолизинг.

С помощью AirFlow один раз в неделю просходит запуск парсеров с последующим построением модели предсказаний цены.

По API можно получить информацию о моделе предсказаний и предикт цены автомобиля.

_____________________________________________________________________________________________

Инструкция по разворачиванию проекта.

1. Сделайте клон репозитория и перейдите в папку с проектом.

2. Выполните команду: 'echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env' например с помощью GIT BASH.

3. Поднимите airflow-init с помощью Docker Сompose: docker-compose up airflow-init.

4. Поднимите Docker Compose для Airflow: docker-compose up.

5. Далее зайдите в командную строку контейнеров и установите нужные для работы пайплайна пакеты (например, scikit-learn):

docker exec -it worker_id bash

pip install scikit-learn 

и 

docker exec -it scheduler_id bash 

pip install scikit-learn

Где worker_id и scheduler_id идентификационные номера данных контейнеров. Также установку библиотеки scikit-learn можно провести непосредственно из программы docker desktop перейдя в данные контейнеры (worker и scheduler), затем выбрав вкладку Exec и в коммандной строке вкладки у обоих контейнеров введя команду pip install scikit-learn.

________________________________________________________________________________________________

Парсинг данных и построение модели предсказаний.

Для запуска задания по парсингу данных и запуску пайплайна для построения модели предсказаний перейдите на веб сервер airflow: 127.0.0.1:8080. Вручную запустите DAG на исполнение.

________________________________________________________________________________________________

Получение предиктов по цене автомобиля.

Введите в адресную строку браузера 127.0.0.1:8000/docs в 

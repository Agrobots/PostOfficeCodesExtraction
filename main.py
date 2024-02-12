# Импортируем необходимые библиотеки для работы с веб-драйвером и парсингом HTML
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re

import logging

# Настройка базового конфига для логирования
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', encoding='utf-8')

# Запись сообщений разного уровня
logging.debug('Это сообщение уровня DEBUG')
logging.info('Это сообщение уровня INFO')
logging.warning('Это сообщение уровня WARNING')
logging.error('Это сообщение уровня ERROR')
logging.critical('Это сообщение уровня CRITICAL')


REPLACE_IN_STREET = "toate"

"""
КОДЫ ПРИДНЕСТРОВЬЯ
https://expertpmr.ru/?rid=4&pid=37
"""


# Путь к драйверу Chrome, который используется для автоматизации браузера
path_to_chromedriver = "chromedriver-win64/chromedriver.exe"
service = Service(executable_path=path_to_chromedriver)
driver = webdriver.Chrome(service=service)
sorted_houses = []

# URL-адреса в разных языковых версиях для последующего скрапинга
source_ro = "https://www.posta.md/ro/map/post_office-"
source_ru = "https://www.posta.md/ru/map/post_office-"
source_en = "https://www.posta.md/en/map/post_office-"


def addresses_nested_dict():
    return defaultdict(addresses_nested_dict)


nested_addresses = addresses_nested_dict()


# Функция для чтения содержимого страницы
def read_content(url):
    driver.get(url)  # Открываем страницу в браузере
    time.sleep(5)
    press_button()   # Вызываем функцию нажатия на кнопку
    time.sleep(2)    # Ждем 5 секунд для полной загрузки страницы
    html = driver.page_source  # Получаем исходный код страницы
    soup = BeautifulSoup(html, "html.parser")  # Используем BeautifulSoup для парсинга HTML
    return soup

def custom_sort(item):
    # Извлекаем числовую часть и буквенную добавку
    number_part = ''.join(char for char in item if char.isdigit())
    letter_part = ''.join(char for char in item if char.isalpha())

    # Преобразуем числовую часть в число для корректной сортировки
    number_part = int(number_part) if number_part else 0

    # Возвращаем кортеж, состоящий из числовой части и буквенной добавки
    return (number_part, letter_part)

# # Функция очистки текста
# def clean_text(string_):
#     words_to_remove = ["toate"]
#     for word in words_to_remove:
#         text = string_.replace(word, "")
#     return string_.strip()


# Функция для нажатия на кнопку на странице
def press_button():
    driver.implicitly_wait(5)  # Устанавливаем неявное ожидание в 5 секунд
    buttons = driver.find_elements(By.CSS_SELECTOR, ".button.button--medium.button--dark")  # Ищем кнопку по селектору
    if len(buttons) > 0:
        for i in range(len(buttons)):
            buttons[i].click()  # Если кнопка найдена, нажимаем на каждую

def extract_numbers(input_string):

    # Удаление пробелов вокруг дефисов для упрощения последующего разделения на диапазоны
    input_string = re.sub(r'\s*-\s*', '-', input_string)

    # Поиск чисел, за которыми следует буква, с возможными пробелами между ними
    with_letters = re.findall(r'\s*\d+\s*[a-zA-Z]', input_string)
    # Поиск чисел, разделённых слешем, с возможными пробелами вокруг слеша
    with_slash = re.findall(r'\s*\d+\s*/\s*\d', input_string)

    # Объединение найденных чисел с буквами и чисел, разделённых слешем, в один список
    extended_numbers = with_slash + with_letters

    # Удаление пробелов из элементов списка extended_numbers
    for i in range(len(extended_numbers)):
        extended_numbers[i] = extended_numbers[i].replace(' ', '')

    # Удаление букв и следующих за ними пробелов из исходной строки для упрощения разделения на числовые диапазоны
    input_string = re.sub(r'\s*[a-zA-Z]', '', input_string)
    # Удаление слешей [и возможных пробелов вокруг них] и последующих чисел из исходной строки
    input_string = re.sub(r'\s*/\s*\d*', '', input_string)

    # Разделение обработанной строки на отдельные элементы по запятым и пробелам, предшествующим числам
    splited = re.split(r',\s+|\s+,|\s+(?=\d+)', input_string)

    new_houses_list = []

    # Обработка каждого элемента разделённой строки
    for i in range(len(splited)):
        # Если элемент содержит дефис, интерпретировать его как числовой диапазон
        if '-' in splited[i]:
            # Извлечение чисел, формирующих диапазон
            for_range = re.findall(r'\d+', splited[i])
            # Создание списка чисел, входящих в диапазон, включая оба конца
            range_list = list(range(int(for_range[0]), int(for_range[1]) + 1))
            # Добавление чисел из диапазона в список домов
            new_houses_list = new_houses_list + range_list
            # Преобразование чисел списка в строки для единообразия с extended_numbers
            new_houses_list = list(map(str, new_houses_list))

    # Объединение всех найденных и сгенерированных номеров домов в один список
    all_houses_list = new_houses_list + extended_numbers
    return all_houses_list

# Функция для извлечения и печати определенных тегов HTML со страницы
def retrieve_html_tags(url, postal_index):
    print(postal_index)
    city = []
    soup = read_content(url)  # Читаем содержимое страницы
    # Ищем и получаем необходимые элементы

    header_2 = soup.find("h2", class_="postal-office__container--title mt-16")
    if header_2:
        municipality_district = header_2.get_text()
        print(municipality_district)

        header_3 = soup.find_all("h3", class_="postal-office__container--subtitle mt-16")

        if header_3:
            for item in header_3:
                city_village = item.get_text()
                print(city_village)
                city.append(city_village)

                wrapper = item.find
                addresses = item.find_all("div", class_="postal-office__container--wrapper")
                print(type(addresses))

                for address in addresses:
                    print(address)
                    street_name = address.find_all("span")
                    print(street_name.get_text())
                    # проверка
                    current_street = street_name[0].get_text()
                    print(current_street)

                    if len(street_name) > 1:
                        # print(list(map(type, [postal_index, municipality_district, city_village])))

                        sorted_houses = sorted(extract_numbers(street_name[1].get_text()), key=custom_sort)
                        print(f"{sorted_houses} sorted 1")

                    else:
                        list_of_elements = current_street.replace(",", " ").replace(", ", " ").split()
                        if any(char.isdigit() for char in list_of_elements[-1]):
                            current_houses = list_of_elements[-1]
                            current_street = current_street.replace(current_houses, "")

                            print(current_street)
                            print(f"{current_houses} sorted 2")




# Функция для извлечения данных со страниц для диапазона почтовых индексов
def retrieve_text_by_postal_index(source, start, stop):
    for postal_index in range(start, stop):
        postal_url = source + str(postal_index)  # Формируем URL
        retrieve_html_tags(postal_url, postal_index)  # Извлекаем и печатаем данные со страницы

# Вызов функции для извлечения данных со страниц на русском языке
retrieve_text_by_postal_index(source_ru, 2069, 2071)

driver.quit()  # Закрываем браузер после выполнения скрипта
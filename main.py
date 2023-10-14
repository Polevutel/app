import requests
import sys
import os
import json
from tqdm import tqdm
from configparser import ConfigParser


class VkAPI:
    def __init__(self, vk_token):
        self.token = vk_token

    # Метод для получения id пользователя по его screen name
    def get_user_id(self, screen_name):
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': self.token,
            'user_ids': screen_name,
            'v': '5.131'
        }
        response = requests.get(url, params=params).json() # делаем запрос на API VK
        user_id = response['response'][0]['id'] # извлекаем user_id из ответа
        return user_id

    # Метод для получения фотографий пользователя
    def get_photos(self, owner_id, album_id, count):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token,
            'owner_id': owner_id,
            'album_id': album_id,
            'count': count,
            'extended': 1, # Запрашиваем расширенную информацию
            'v': '5.131'
        }
        response = requests.get(url, params=params).json() # делаем запрос на API VK
        photos = response['response']['items'] # извлекаем информацию о фотографиях
        return photos


class YandexDiskAPI:
    def __init__(self, yandex_disk_token):
        self.token = yandex_disk_token

    # Метод для создания папки на Yandex Disk
    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {
            'path': folder_name
        }
        response = requests.put(url, headers=headers, params=params) # делаем запрос на API Yandex Disk для создания папки

    # Метод для загрузки фотографии на Yandex Disk
    def upload_photo(self, photo_url, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {
            'path': folder_name + '/' + file_name,
            'url': photo_url,
            'overwrite': True # параметр, указывающий на необходимость перезаписи файла, если он уже существует
        }
        response = requests.post(url, headers=headers, params=params) # делаем запрос на API Yandex Disk для загрузки фото


# Функция для сохранения результатов в json файл
def save_results_to_json(results, json_file):
    with open(json_file, 'w') as file:
        json.dump(results, file) # записываем данные в файл в формате json

# Функция для чтения конфигурационного файла
def read_config(file_path):
    config = ConfigParser()
    config.read(file_path)
    vk_token = config.get('Tokens', 'VK_TOKEN')
    yandex_disk_token = config.get('Tokens', 'YANDEX_DISK_TOKEN')
    return vk_token, yandex_disk_token

# Запуск главной части программы

if __name__ == '__main__':
    owner = input('Введите ID  профиля VK: ')
    count = int(input('Введите количество загружаемых фотографий: '))
    config_file = input('Введите путь к файлу с токенами: ')

    vk_token, yandex_disk_token = read_config(config_file) # Читаем токены из файла конфигурации

    vk_api = VkAPI(vk_token) # Создаем объекты классов VkAPI и YandexDiskAPI
    yandex_disk_api = YandexDiskAPI(yandex_disk_token)

    if owner.isdigit():
        owner_id = owner
    else:
        owner_id = vk_api.get_user_id(owner)

    album_id = 'wall'  # Задаем ID альбома 
    photos = vk_api.get_photos(owner_id, album_id, count)

    results = []

    folder_name = 'VK Photos'
    yandex_disk_api.create_folder(folder_name)

    for photo in tqdm(photos, file=sys.stdout):
        likes = photo['likes']['count']
        largest_size = max(photo['sizes'], key=lambda x: x['width'])
        photo_url = largest_size['url']
        file_name = f'{likes}.jpg'
        yandex_disk_api.upload_photo(photo_url, folder_name, file_name)
        
        result = {
            'file_name': file_name,
            'size': largest_size
        }
        results.append(result)

    save_results_to_json(results, 'results.json')

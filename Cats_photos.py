import requests
from pprint import pprint

from settings import TOKEN
import time


class Cataas:
    def __init__(self, text):
        self.text = text

    def download_cat_photos(self):
        print('Получаем ссылку на картинку, подождите....')
        url = f'https://cataas.com/cat/says/{self.text}'
        response = requests.get(url)

        if response.status_code == 200:
            print(
                'Формируем имя файла из ссылки '
                'для сохранения на яндекс диск, подождите....'
            )
            filename = self.text.strip().replace(' ', '_')
            for symbol in '/\\:*?"<>|':
                filename = filename.replace(symbol, '')
            filename = f'{filename}.jpg'
            print(f'Имя файла: {filename}')

            return response.url, filename
        else:
            print(f'Ошибка при получении картинки: {response.status_code}')
        return None, None


class YandexDisc:
    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}
        self.base_url = 'https://cloud-api.yandex.net'

    def create_folder(self, path):
        print('Создаем папку на Яндекс Диск, подождите.....')
        response = requests.put(
            f'{self.base_url}/v1/disk/resources',
            headers=self.headers,
            params={'path': path},
        )

        if response.status_code == 409:
            print(
                f'Статус код: {response.status_code}. '
                'Папка с таким именем была создана ранее.'
            )
        elif response.status_code == 201:
            print(f'Статус код: {response.status_code}. Папка создана успешно.')
        else:
            print(
                f'Статус код: {response.status_code}. '
                'Попробуйте повторить попытку позже.'
            )

        return response.status_code

    def upload_file(self, path_file, path_yd):
        print('Загружаем файл на Яндекс Диск, подождите....')
        response = requests.post(
            f'{self.base_url}/v1/disk/resources/upload',
            headers=self.headers,
            params={
                'url': path_file,
                'path': path_yd,
            },
        )


        if response.status_code == 403:
            print(
                f'Статус код: {response.status_code}. '
                'На Вашем диске недостаточно места. '
                'Удалите лишнее или увеличьте объём Диска.'
            )
        elif response.status_code == 409:
            print(
                f'Статус код: {response.status_code}. '
                'Файл с таким именем уже существует.'
            )
        elif response.status_code == 202:
            print(f'Статус код: {response.status_code}. Файл в процессе загрузки...')
            op_id = (response.json()['href'].split('/')[-1])

        else:
            print(
                f'Статус код: {response.status_code}. '
                'Попробуйте повторить попытку позже.'
            )

        return response.status_code, op_id

    def get_status (self, operation_id):
        print('Проверяем статус загрузки, подождите...')
        response = requests.get(
        f'{self.base_url}/v1/disk/operations/{operation_id}',
        headers=self.headers
                             )
        if response.status_code == 200 and response.json()['status'] == 'success':
            print(f'Статус код: {response.status_code},{response.json()}.'
                  f'Файл загружен успешно')
        else:
            print('Что-то пошло не так')

        return response.status_code, response.json()['status']

    def files_info(self, path):
        print('Получаем информацию о загруженных файлах, подождите...')
        response = requests.get(
            f'{self.base_url}/v1/disk/resources',
            headers=self.headers,
            params={'path': path}
        )


        if response.status_code == 200:
            print(
                f'Статус код: {response.status_code}. '
                'Информация получена, идет обработка, подождите....'
            )
            response_data = response.json()
            filtered_list = []


            for item in response_data['_embedded']['items']:
                clean_item = {
                    'size': item.get('size'),
                    'path': item.get('path'),
                    'name': item.get('name'),
                    'created': item.get('created')
                }
                filtered_list.append(clean_item)

            pprint(filtered_list)
        else:
            print(
                f'Статус код: {response.status_code}. '
                'Попробуйте повторить попытку позже.'
            )

        return response.status_code, filtered_list


class WriteFiles:
    def __init__(self, data_file):
        self.data_file = data_file

    def save_to_json(self):
        import json

        print('Производим запись данных с Яндекс Диск в файл, подождите...')
        with open('image_cat10.json', 'w', encoding='utf-8') as file:
            json.dump(self.data_file, file, ensure_ascii=False, indent=4)
        print('Файл записан успешно')


def main():
    text_input = input(
        'Введите текст для картинки, '
        'желательно без пробелов и спецсимволов: '
    )
    # Создаем экземпляр класса Cataas
    # Вызываем метод получения ссылки на картинку кота с текстом
    getcats = Cataas(text_input)
    url, filename = getcats.download_cat_photos()
    #
    if not url or not filename:
        return

    # Просим пользователя ввести имя папки в которую сохраним файл
    folder = input('Введите название папки для Яндекс Диск: ')
    yd = YandexDisc(TOKEN)
    yd.create_folder(f'{folder}')

    code, op_id = yd.upload_file(url, f'{folder}/{filename}')
    time.sleep(3)

    code, status = yd.get_status(op_id)

    status_code, filtered_list = yd.files_info(f'{folder}')


    writer = WriteFiles(filtered_list)
    writer.save_to_json()


if __name__ == '__main__':
    main()
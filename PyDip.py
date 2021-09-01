import requests
import datetime
import json
import os
from pprint import pprint
from abc import ABCMeta, abstractmethod
from settings import *


class Disk:
    __metaclass__ = ABCMeta

    def __init__(self, token: str):
        self.token = token

    @abstractmethod
    def title(self):
        """информация о диске"""
        pass

    @abstractmethod
    def get_resources(self, path):
        """Метод получает информацию и возращает код о результате запроса 'path'"""
        pass

    @abstractmethod
    def create_directory(self, directory: str):
        """Метод создаёт дерикторию 'directory'"""
        pass

    @abstractmethod
    def upload_by_url(self, url: str, file: str, path=''):
        """Загрузка по URL"""
        pass

    def create_path(self, path: str):
        """Метод создаёт дерикторию 'path'"""
        path_ = ''
        for directory in path.split('/'):
            path_ += directory + '/'
            cod = self.create_directory(path_)
            if cod is False:
                return cod
        return cod

    def upload_file_by_url(self, file_info: dict, path=''):
        """Метод загружает файлы из словаря'file_info' ={'url': ,'likes': ,'size': ,'date': ,'exp': }
         на яндекс диск, в дерикторию'path'"""
        file_name = file_info['likes'] + file_info['exp']
        while True:
            print(f'Начинается копирование файлов на "{self.title()}"')
            cod = self.get_resources(path + file_name)
            if cod == 404:
                cod = self.upload_by_url(file_info['url'], file_name, path)
            elif cod == 200:
                file_name = file_info['likes'] + file_info['date'] + '_' + file_info['exp']
                cod = self.upload_by_url(file_info['url'], file_name, path)
            else:
                print(f'{str_red}mЗапрос на наличие "{path + "/" + file_name}" вернул ошибку. ОШИБКА: "{cod}"'
                      f'{str_reset}')
                return False
            if cod != 202:
                print(f'{str_red}Загрузка файла по адкресу:\n"{file_info["url"]}"\n на яндекс диск не удалась. '
                      f'ОШИБКА: "{cod}"{str_reset}')
                return False
            else:
                print(f'{str_green}Файл по адресу:\n"{file_info["url"]}"\n загружен на яндекс диск в дерикторию '
                      f'"{path + "/" + file_name}"{str_reset}')
                return [{"file_name": file_name, "size": file_info['size']}]


# API Яндекс.Диска
class YDisk(Disk):
    API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, token: str):
        super().__init__(token)
        self.headers = {'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def title(self):
        s = 'Облачное хранилище: "Яндекс.Диск"'
        return s

    def disc(self):
        """Получить метаинформацию пользователя диска"""
        resp = requests.get(self.API_BASE_URL + 'resources/files', headers=self.headers)
        pprint(resp.json())

    def get_resources(self, path):
        """Метод получает информацию и возращает код о результате запроса 'path'"""
        headers = self.headers.copy()
        resp = requests.get(self.API_BASE_URL + 'resources', headers=headers,
                            params={'path': path, 'fields': 'name'})
        return resp.status_code

    def create_directory(self, directory: str):
        """Метод создаёт дерикторию 'directory'"""
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        resp = requests.put(self.API_BASE_URL + 'resources', headers=headers, params={'path': directory})
        cod = resp.status_code
        if cod == 201:
            print(f'{str_purple}Папка, "{directory}", успешно созданна{str_reset}')
            return True
        elif cod == 409:
            print(f'{str_purple}Дериктория, "{directory}", уже была созданна{str_reset}')
            return cod
        else:
            print(f'{str_red}Ошибка: {cod}{str_reset}')
            return False

    def upload(self, file_path: str, file_name: str, path=''):
        """Метод загружает файл 'file_path' на яндекс диск. """
        headers = self.headers.copy()
        params = {'path': path + '/' + file_name}
        resp = requests.get(self.API_BASE_URL + 'resources/upload', headers=headers, params=params)
        cod = resp.status_code
        if cod != 200:
            print(f'{str_red}Ссылка для загрузки файла "{file_name}" на яндекс не получена. ОШИБКА: "{cod}"{str_reset}')
            return False
        upload_url = resp.json()['href']
        resp = requests.put(upload_url, headers=headers, files={"file": open(file_path, 'rb')})
        cod = resp.status_code
        if cod != 201:
            print(f'{str_red}Загрузка файла "{file_name}" на яндекс диск не удалась. ОШИБКА: "{cod}"{str_reset}')
            return False
        else:
            print(f'{str_green}Файл загружен на яндекс диск в дерикторию "{path}/{file_name}"{str_reset}')
            return True

    def upload_by_url(self, url: str, file: str, path=''):
        """Загрузка по URL"""
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        path += '/' + file
        params = {'url': url, 'path': path}
        resp = requests.post(self.API_BASE_URL + 'resources/upload', headers=headers, params=params)
        return resp.status_code


class GoogleDisk(Disk):
    API_BASE_URL = 'https://www.googleapis.com/drive/v3/'

    def __init__(self, token: str):
        super().__init__(token)
        self.headers = {'Accept': 'application/json', 'Authorization': f'Bearer  {self.token}'}

    def title(self):
        s = 'Облачное хранилище: "Google.Диск"'
        return s

    def get_resources(self, path):
        """Метод получает информацию и возращает код о результате запроса 'path'"""
        pass

    def create_directory(self, directory: str):
        """Метод создаёт дерикторию 'directory'"""
        pass

    def upload_by_url(self, url: str, file: str, path=''):
        """Загрузка по URL"""
        pass


class SocialNetwork:
    __metaclass__ = ABCMeta

    def __init__(self, token: str):
        self.token = token

    @abstractmethod
    def title(self):
        """информация о соц. сети"""
        pass

    @abstractmethod
    def photos_get_max_param(self, owner_id=None, param='profile', count=5, offset=0):
        pass

    def get_url(self, type_file=1, user_ip=None, count=5, album='profile', offset=0):
        if type_file == '1':
            return self.photos_get_max_param(user_ip, album, count, offset)


class VK(SocialNetwork):
    API_BASE_URL = 'https://api.vk.com/method/'
    ip_list = 'ip_list_VK.txt'

    def __init__(self, token: str):
        super().__init__(token)
        self.params = {'access_token': {self.token},
                       'v': '5.131'}

    def title(self):
        s = 'Соц. сеть: "ВКонтакте"'
        return s

    def users_get(self, user_id=None):
        params = self.params
        params.update({'user_id': user_id})
        resp = requests.get(self.API_BASE_URL + 'users.get', params=params)
        return resp.json()

    def photos_get(self, owner_id=None, album_id='profile', count=5, offset=0):
        params = self.params
        params.update({'owner_id': owner_id,
                       'album_id': album_id,
                       'rev': 1,
                       'extended': 1,
                       'offset': offset,
                       'count': count,
                       'photo_sizes': 1})
        resp = requests.get(self.API_BASE_URL + 'photos.get', params=params)
        return resp.json()

    def photos_get_user_photos(self, user_id=None, count=5, offset=0):
        params = self.params
        params.update({'user_id': user_id,
                       'sort': 0,
                       'extended': 1,
                       'offset': offset,
                       'count': count,
                       'photo_sizes': 1})
        resp = requests.get(self.API_BASE_URL + 'photos.getUserPhotos', params=params)
        return resp.json()

    def photos_get_all(self, owner_id=None, count=5, offset=0):
        params = self.params
        params.update({'owner_id': owner_id,
                       'extended': 1,
                       'offset': offset,
                       'count': count,
                       'photo_sizes': 1,
                       'no_service_albums': 0,
                       'need_hidden': 0,
                       'skip_hidden': 0})
        resp = requests.get(self.API_BASE_URL + 'photos.getAll', params=params)
        return resp.json()

    def photos_get_max_param(self, owner_id=None, param='profile', count=5, offset=0):
        photos_info = []
        if param == 'user_photos':
            resp = self.photos_get_user_photos(owner_id, count, offset)
        else:
            resp = self.photos_get(owner_id, param, count, offset)
        print(f'{str_yellow}IP "{owner_id}": {self.user_name(owner_id)}\nПолученые URL для скачивания:{str_reset}')
        if 'response' in resp:
            i = 0
            for photo_info in resp['response']['items']:
                photos_info += [{'url': photo_info['sizes'][-1]['url'],
                                 'size': photo_info['sizes'][-1]['type'],
                                 'likes': str(photo_info['likes']['count']),
                                 'exp': '.jpg',
                                 'date': str(photo_info['date'])}]
                i += 1
                print(f"\t{i}).{photo_info['sizes'][-1]['url']}\n")
            if len(photos_info) == 0:
                print('По запросу фотографий не найденно')
            return photos_info
        else:
            error = {'error': {'error_code': resp['error']['error_code'],
                               'error_msg': resp['error']['error_msg']}}
            print(f"{str_red}Ошибка при запроссе к IP:'{owner_id}'\n{error['error']}{str_reset}")
            return False

    def user_name(self, user_id=None):
        return self.users_get(user_id)['response'][0]['first_name'] + '_' + self.users_get(user_id)['response'][0][
            'last_name']


def current_date_str():
    current_date = datetime.datetime.now()
    return current_date.strftime('%y_%m_%d %H_%M_%S')


def read_file(path: str):
    with open(path, encoding='utf-8') as f:
        res = f.read().strip()
    return res


def write_json(file_info, path: str):
    with open(path, 'w', encoding='utf-8', ) as f:
        res = json.dump(file_info, f, ensure_ascii=False, indent=2)
        return res


class UserInterface:
    def __init__(self):
        self.q_dict = {'q': {'command': self.exit_, 'param': None}}
        self.b_s_dict = {'b': {'command': self.back_, 'param': None},
                         's': {'command': self.start_menu, 'param': None}}

    def input_(self, param=None):
        print(param)
        return input()

    def equally_(self, param):
        return param

    def back_(self, param=None):
        print(param)
        return False

    def exit_(self, param='До новых встреч!!!'):
        if param is None:
            param = 'До новых встреч!!!'
        print(f'\n{str_turquoise}{str_fat}{str_italics}{param}\n{str_reset}')
        return exit()

    def command_table(self, commands: list):  # создаём таблицу
        def str_table(x0, x1, x2, x3, x4):
            print('{0}{1:^10}{2}{3:<40}{4}'.format(x0, x1, x2, x3, x4))

        str_table(chr(int('250F', 16)), chr(int('2501', 16)) * 10, chr(int('2533', 16)), chr(int('2501', 16)) * 40,
                  chr(int('2513', 16)))
        str_table(chr(int('2503', 16)), 'Команда', chr(int('2503', 16)), 'Описание операции'.center(40),
                  chr(int('2503', 16)))
        # with open(path, encoding='utf-8', ) as f:
        #     commands = json.load(f)
        for command in commands:
            str_table(chr(int('2523', 16)), chr(int('2501', 16)) * 10, chr(int('254B', 16)), chr(int('2501', 16)) * 40,
                      chr(int('252B', 16)))
            str_table(chr(int('2503', 16)), command['command'], chr(int('2503', 16)), command['description'],
                      chr(int('2503', 16)))
        str_table(chr(int('2517', 16)), chr(int('2501', 16)) * 10, chr(int('253B', 16)), chr(int('2501', 16)) * 40,
                  chr(int('251B', 16)))

    def command_request(self, input_dict: dict, s='\nВведите команду: ', key=True):  # Запроскоманд
        command = input(s).lower()
        print()
        if command in input_dict:
            return input_dict[command]['command'](input_dict[command]['param'])
        elif key:
            print(f'\n{str_red}Команда не определена{str_reset}\n')
            return self.command_request(input_dict)
        else:
            return command

    def connect_social_networks(self):  # Выбор социальной сети
        input_dict = {**{'1': {'command': VK, 'param': TOKEN_VK, },
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_social_network)
        return self.command_request(input_dict)

    def connect_disk(self):  # Выбор диска
        input_dict = {**{'1': {'command': YDisk, 'param': TOKEN_YN},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_disk)
        return self.command_request(input_dict)

    def users_ip(self, ip_list=None):  # Ввод списка IP адресов
        input_dict = {**{'1': {'command': self.input_, 'param': 'Введите IP через пробел'},
                         '2': {'command': read_file, 'param': ip_list},
                         '': {'command': self.equally_, 'param': [None]},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_users_ip)
        result = self.command_request(input_dict)
        if type(result) is str:
            return result.split()
        else:
            return result

    def type_file_(self):  # Выбор типа файлов
        input_dict = {**{'1': {'command': self.equally_, 'param': '1'},
                         '': {'command': self.equally_, 'param': '1'},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_type_file)
        return self.command_request(input_dict, '\nВведите команду(по умолчанию "Фотографии"): ')

    def count_(self):  # Ввод количества файлов
        input_dict = {**{'': {'command': self.equally_, 'param': '5'},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_count)
        return self.command_request(input_dict, '\nВведите количество последних загружаемых файлов(по умолчанию "5"): ',
                                    key=False)

    def album_(self):
        albums = {'1': 'profile', '2': 'wall', '3': 'user_photos'}
        input_dict = {**{'1': {'command': self.equally_, 'param': albums['1']},
                         '2': {'command': self.equally_, 'param': albums['2']},
                         '3': {'command': self.equally_, 'param': albums['3']},
                         '': {'command': self.equally_, 'param': albums['1']},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_album)
        return self.command_request(input_dict,
                                    '\nВведите название альбомаба(по умолчанию "из профиля") или введите команду: ',
                                    key=False)

    def path_(self):  # Ввод количества файлов
        input_dict = {**{'': {'command': self.equally_, 'param': 'download/'},
                         **self.b_s_dict, **self.q_dict}}
        self.command_table(commands_path_save)
        return self.command_request(input_dict,
                                    '\nВведите путь для сохранения файлов(по умолчанию "/download/" + '
                                    '<дата_скачивания>/<имя_владельца IP>/"): ',
                                    key=False)

    def request_(self, request='Введите команду'):
        input_dict = {'yes': {'command': self.equally_, 'param': True},
                      'no':  {'command': self.equally_, 'param': False}}
        return self.command_request(input_dict, request)

    def start_menu(self, param=None):
        if param is not None:
            print(param)
        input_dict = {**{'1': {'command': self.save_files_to_disk, 'param': None},
                         **self.q_dict}}
        self.command_table(commands_start)
        return self.command_request(input_dict)

    def save_files_to_disk(self, params=None):
        social_networks = True
        while social_networks:
            social_networks = self.connect_social_networks()
            disk = True
            while social_networks and disk:
                print(f'Социальная сеть: {str_blue}{type(social_networks).__name__}\n\033[0m')
                disk = self.connect_disk()
                users = True
                while disk and users is not False:
                    print(f'Диск: {str_blue}{type(disk).__name__}\n{str_reset}')
                    users = self.users_ip(social_networks.ip_list)
                    type_file = True
                    while users is not False and type_file:
                        print(f'IP: {str_blue}{users}\n{str_reset}')
                        type_file = self.type_file_()
                        count = True
                        while type_file and count:
                            print(f'Тип файлов: {str_blue}{type_file}\n{str_reset}')
                            count = self.count_()
                            album = True
                            while count and album:
                                print(f'Колличество: {str_blue}{count}\n{str_reset}')
                                album = self.album_()
                                path = True
                                while album and path:
                                    print(f'Альбом: {str_blue}{album}\n{str_reset}')
                                    path = self.path_()
                                    while path:
                                        print(
                                            f'Путь для сохранения: {str_blue}{disk.title()}: {path}  +  '
                                            f'<дата_скачивания>/<имя_владельца IP>/{str_reset}')
                                        for user in users:
                                            files_info = social_networks.get_url(type_file, user, count, album)
                                            if files_info:
                                                address = path + social_networks.user_name(
                                                    user) + '/' + current_date_str()
                                                cod = disk.create_path(address)
                                                if cod is not False:
                                                    while True:
                                                        files_info_error = []
                                                        for file_info in files_info:
                                                            res_info = disk.upload_file_by_url(file_info, address)
                                                            if res_info:
                                                                file_name = res_info[0]['file_name'].rsplit('.', 1)[
                                                                                0] + '.json'
                                                                temp = 'TEMP/' + file_name
                                                                write_json(res_info, temp)
                                                                if disk.upload(temp, file_name, address):
                                                                    os.remove(temp)
                                                            else:
                                                                files_info_error += file_info
                                                        if len(files_info_error) != 0:
                                                            print('Следующие файлы не получилось сохранить:')
                                                            pprint(files_info_error)
                                                            files_info = files_info_error
                                                        else:
                                                            break
                                                        if not self.request_(
                                                                '\nПопробовать сохранить ещё раз(yes/no: '):
                                                            break
                                        print()
                                        return self.save_files_to_disk()

        return self.start_menu('\nВозврат в стартовоеменю\n')


if __name__ == '__main__':
    # Получить токен от пользователя из файла
    TOKEN_VK = read_file('tokens/token API_VK.txt')
    TOKEN_YN = read_file('tokens/token API_Yandex.txt')

    c = UserInterface()
    c.start_menu()

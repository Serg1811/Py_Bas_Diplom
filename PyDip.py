import datetime
import json
import os
from pprint import pprint
import requests


class Disk:

    def __init__(self, token: str):
        self.token = token

    def create_path(self, path: str):
        """Метод создаёт дерикторию 'path'"""
        path_ = ''
        for directory in path.split('/'):
            path_ += directory + '/'
            cod = self.create_directory(path_)
            if cod == False:
                return cod
        return cod

    def upload_file_by_url(self, file_info: dict, path=''):
        """Метод загружает файлы из словаря'file_info' ={'url': ,'likes': ,'size': ,'date': ,'exp': } на яндекс диск, в дерикторию'path'"""
        file_name = file_info['likes'] + file_info['exp']
        while True:
            print(f'Начинается копирование файлов на "{self.title}"')
            cod = self.get_resurses(path + file_name)
            if cod == 404:
                cod = self.upload_by_url(file_info['url'], file_name, path)
            elif cod == 200:
                file_name = file_info['likes'] + file_info['date'] + '_' + file_info['exp']
                cod = self.upload_by_url(file_info['url'], file_name, path)
            else:
                print('\033[31mзапрос на наличие "{0}" вернул ошибку. ОШИБКА: "{1}"\033[0m'.format(path + '/' + file_name, cod))
                return False
            if cod != 202:
                print('\033[31mЗагрузка файла по адкресу:\n"{0}"\n на яндекс диск не удалась. ОШИБКА: "{1}"\033[0m'.format(file_info["url"], cod))
                return False
            else:
                print('\033[35mФайл по адресу:\n"{0}"\n загружен на яндекс диск в дерикторию "{1}"\033[0m'.format(file_info["url"], path + '/' + file_name))
                return [{"file_name": file_name, "size": file_info['size']}]


#API Яндекс.Диска
class YDisk(Disk):

    API_BASE_URL = 'https://cloud-api.yandex.net/'

    def __init__(self, token: str):
        super().__init__(token)
        self.headers = {'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def title(self):
        s = 'Одлачное хранилище: "Яндекс.Диск"'
        return s

    def disc(self):
        """Получить метаинформацию пользователя диска"""
        resp = requests.get(self.API_BASE_URL + 'v1/disk/resources/files', headers=self.headers)
        pprint(resp.json())

    def get_resurses(self, path):
        """Метод получает информацию и возращает код о результате запроса 'path'"""
        headers = self.headers.copy()
        resp = requests.get(self.API_BASE_URL + 'v1/disk/resources', headers=headers, params={'path': path, 'fields': 'name'})
        return resp.status_code

    def create_directory(self, directory: str):
        """Метод создаёт дерикторию 'directory'"""
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        resp = requests.put(self.API_BASE_URL + 'v1/disk/resources', headers=headers, params={'path': directory})
        cod = resp.status_code
        if cod == 201:
            print(f'\033[35mПапка, "{directory}", успешно созданна\033[0m')
            return True
        elif cod == 409:
            print(f'\033[35mДериктория, "{directory}", уже была созданна\033[0m')
            return cod
        else:
            print(f'\033[31mОшибка: {cod}\033[0m')
            return False

    def upload(self, file_path: str, file_name: str, path=''):
        """Метод загружает файл 'file_path' на яндекс диск. """
        headers = self.headers.copy()
        params = {'path': path + '/' + file_name}
        resp = requests.get(self.API_BASE_URL + 'v1/disk/resources/upload', headers=headers, params=params)
        cod = resp.status_code
        if cod != 200:
            print(f'\033[31mСсылка для загрузки файла "{file_name}" на яндекс не получена. ОШИБКА: "{cod}"\033[0m')
            return False
        upload_url = resp.json()['href']
        resp = requests.put(upload_url, headers=headers, files={"file": open(file_path, 'rb')})
        cod = resp.status_code
        if cod != 201:
            print(f'\033[31mЗагрузка файла "{file_name}" на яндекс диск не удалась. ОШИБКА: "{cod}"\033[0m')
            return False
        else:
            print(f'\033[35mФайл загружен на яндекс диск в дерикторию "{path}/{file_name}"\033[0m')
            return True

    def upload_by_url(self, url: str, file: str, path=''):
        """Загрузка по URL"""
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        path += '/' + file
        params = {'url': url, 'path': path}
        resp = requests.post(self.API_BASE_URL + 'v1/disk/resources/upload', headers=headers, params=params)
        return resp.status_code



class SocialNetwork:

    def __init__(self, token: str):
        self.token = token

    def GetUrl(self, type_file=1, userIP=None, count=5, albom='profile', offset=0):
        if type_file == '1':
            return self.PhotosGetMaxParam(userIP, albom, count, offset)



class VK(SocialNetwork):

    API_BASE_URL = 'https://api.vk.com/method/'
    ip_list = 'ip_list_VK.txt'

    def __init__(self, token: str):
        super().__init__(token)

    def title(self):
        s = 'Соц. сеть: "ВКонтакте"'
        return s

    def users_get(self, user_id=None):
        params = {'access_token': {self.token},
                  'v': '5.131',
                  'user_id': user_id}
        resp = requests.get(self.API_BASE_URL + 'users.get', params=params)
        return resp.json()

    def photos_get(self, owner_id=None, album_id='profile', count=5, offset=0):
        params = {'access_token': f'{self.token}',
                  'v': '5.131',
                  'owner_id': owner_id,
                  'album_id': album_id,
                  'rev': 1,
                  'extended': 1,
                  'offset': offset,
                  'count': count,
                  'photo_sizes': 1}
        resp = requests.get(self.API_BASE_URL + 'photos.get', params=params)
        return resp.json()

    def photos_getuserphotos(self, user_id=None, count=5, offset=0):
        params = {'access_token': f'{self.token}',
                  'v': '5.131',
                  'user_id': user_id,
                  'sort': 0,
                  'extended': 1,
                  'offset': offset,
                  'count': count,
                  'photo_sizes': 1}
        resp = requests.get(self.API_BASE_URL + 'photos.getUserPhotos', params=params)

        return resp.json()

    def photos_getall(self, owner_id=None, count=5, offset=0):
        params = {'access_token': f'{self.token}',
                  'v': '5.131',
                  'owner_id': owner_id,
                  'extended': 1,
                  'offset': offset,
                  'count': count,
                  'photo_sizes': 1,
                  'no_service_albums': 0,
                  'need_hidden': 0,
                  'skip_hidden': 0}
        resp = requests.get(self.API_BASE_URL + 'photos.getAll', params=params)
        # cod = resp.status_code
        return resp.json()

    def PhotosGetMaxParam(self, owner_id=None, param='profile', count=5, offset=0):
        photos_info = []
        if param == 'userphotos':
            resp = self.photos_getuserphotos(owner_id, count, offset)
        else:
            resp = self.photos_get(owner_id, param, count, offset)
        print(f'\033[32m\033[5mIP "{owner_id}": {self.user_name(owner_id)}\nПолученые URL для скачивания:\033[0m')
        try:
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
        except:
            error = {'error': {'error_code': resp['error']['error_code'],
                                      'error_msg': resp['error']['error_msg']}}
            print("\033[31mОшибка при запроссе к IP:'{0}'\n{1}\033[0m".format(owner_id, error['error']))
            return False

    def user_name(self, user_id=None):
        return self.users_get(user_id)['response'][0]['first_name'] + '_' + self.users_get(user_id)['response'][0]['last_name']


def current_date_str():
    current_date = datetime.datetime.now()
    return current_date.strftime('%y_%m_%d %H_%M_%S')

def read_file(path: str):
    with open(path, encoding='utf-8') as f:
        res = f.read().strip()
    return res

def write_json(file_info, path: str):
    with open(path, 'w', encoding='utf-8',) as f:
        res = json.dump(file_info, f, ensure_ascii=False, indent=2)
        return res


class UserInterface:

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
        print(f'\n\033[36m\033[1m\033[3m{param}\n\033[0m')
        return exit()

    def command_tabl(self, path: str):#создаём таблицу
        def str_tabl(x0, x1, x2, x3, x4):
            print('{0}{1:^10}{2}{3:<40}{4}'.format(x0, x1, x2, x3, x4))

        str_tabl(chr(int('250F', 16)), chr(int('2501', 16))*10, chr(int('2533', 16)), chr(int('2501', 16))*40, chr(int('2513', 16)))
        str_tabl(chr(int('2503', 16)), 'Команда', chr(int('2503', 16)), 'Описание операции'.center(40), chr(int('2503', 16)))
        with open(path, encoding='utf-8', ) as f:
            commands = json.load(f)
        for command in commands:
            str_tabl(chr(int('2523', 16)), chr(int('2501', 16))*10, chr(int('254B', 16)), chr(int('2501', 16))*40, chr(int('252B', 16)))
            str_tabl(chr(int('2503', 16)), command['command'], chr(int('2503', 16)), command['description'], chr(int('2503', 16)))
        str_tabl(chr(int('2517', 16)), chr(int('2501', 16))*10, chr(int('253B', 16)), chr(int('2501', 16))*40, chr(int('251B', 16)))


    def command_request(self, inputDict: dict, s='\nВведите команду: ', key=True):#Запроскоманд
        command = input(s).lower()
        print()
        if command in inputDict:
            return inputDict[command]['command'](inputDict[command]['param'])
        elif key:
            print('\n\033[31m\033[5mКоманда не определена\033[0m\n')
            return self.command_request(inputDict)
        else:
            return command

    def connect_social_networks(self):#Выбор социальной сети
        inputDict = {'1': {'command': VK, 'param': TOKEN_VK, },
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_Social_Network.json')
        return self.command_request(inputDict)

    def connect_disk(self):#Выбор диска
        inputDict = {'1': {'command': YDisk, 'param': TOKEN_YN},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_Disk.json')
        return self.command_request(inputDict)

    def users_ip(self, ip_list=None):#Ввод списка IP адресов
        inputDict = {'1': {'command': self.input_, 'param': 'Введите IP через пробел'},
                     '2': {'command': read_file, 'param': ip_list},
                     '': {'command': self.equally_, 'param': [None]},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_Users_IP.json')
        result = self.command_request(inputDict)
        try:
            return result.split()
        except:
            return result

    def type_file_(self):#Выбор типа файлов
        inputDict = {'1': {'command': self.equally_, 'param': '1'},
                     '': {'command': self.equally_, 'param': '1'},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_type_file.json')
        return self.command_request(inputDict, '\nВведите команду(по умолчанию "Фотографии"): ')

    def count_(self):#Ввод количества файлов
        inputDict = {'': {'command': self.equally_, 'param': '5'},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_count.json')
        return self.command_request(inputDict, '\nВведите количество последних загружаемых файлов(по умолчанию "5"): ', key=False)

    def albom_(self):
        alboms = {'1': 'profile', '2': 'wall', '3': 'userphotos'}
        inputDict = {'1': {'command': self.equally_, 'param': alboms['1']},
                     '2': {'command': self.equally_, 'param': alboms['2']},
                     '3': {'command': self.equally_, 'param': alboms['3']},
                     '': {'command': self.equally_, 'param': alboms['1']},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_albom.json')
        return self.command_request(inputDict, '\nВведите название альбомаба(по умолчанию "из профиля") или введите команду: ', key=False)

    def path_(self):#Ввод количества файлов
        inputDict = {'': {'command': self.equally_, 'param': 'download/'},
                     'q': {'command': self.exit_, 'param': None},
                     'b': {'command': self.back_, 'param': None},
                     's': {'command': self.StartMenu, 'param': None}}
        self.command_tabl('json/commands_count.json')
        return self.command_request(inputDict, '\nВведите путь для сохранения файлов(по умолчанию "/download/" + <дата_скачивания>/<имя_владельца IP>/"): ', key=False)

    def request_(self, request='Введите команду'):
        inputDict = {'yes': {'command': self.equally_, 'param': True},
                     'no': {'command': self.equally_, 'param': False}}
        return self.command_request(inputDict, request)
    def StartMenu(self, param=None):
        if param is not None:
            print(param)
        inputDict = {'1': {'command': self.SaveFilesToDisk, 'param': None},
                     'q': {'command': self.exit_, 'param': None}}
        self.command_tabl('json/commands_Start.json')
        return self.command_request(inputDict)

    def SaveFilesToDisk(self, params=None):
        social_networks = True
        while social_networks:
            social_networks = self.connect_social_networks()
            disk = True
            while social_networks and disk:
                print(f'Социальная сеть: \033[34m\033[5m{type(social_networks).__name__}\n\033[0m')
                disk = self.connect_disk()
                users = True
                while disk and users is not False:
                    print(f'Диск: \033[34m\033[5m{type(disk).__name__}\n\033[0m')
                    users = self.users_ip(social_networks.ip_list)
                    type_file = True
                    while users is not False and type_file:
                        print(f'IP: \033[34m\033[5m{users}\n\033[0m')
                        type_file = self.type_file_()
                        count = True
                        while type_file and count:
                            print(f'Тип файлов: \033[34m\033[5m{type_file}\n\033[0m')
                            count = self.count_()
                            albom = True
                            while count and albom:
                                print(f'Колличество: \033[34m\033[5m{count}\n\033[0m')
                                albom = self.albom_()
                                path = True
                                while albom and path:
                                    print(f'Альбом: \033[34m\033[5m{albom}\n\033[0m')
                                    path = self.path_()
                                    while path:
                                        print(f'Путь для сохранения: \033[34m\033[5m{disk.title()}: {path}  +  <дата_скачивания>/<имя_владельца IP>/\n\033[0m')
                                        for user in users:
                                            files_info = social_networks.GetUrl(type_file, user, count, albom)
                                            if files_info:
                                                adres = path + social_networks.user_name(user) + '/' + current_date_str()
                                                cod = disk.create_path(adres)
                                                if cod is not False:
                                                    while True:
                                                        files_info_error = []
                                                        for file_info in files_info:
                                                            res_info = disk.upload_file_by_url(file_info, adres)
                                                            if res_info:
                                                                file_name = res_info[0]['file_name'].rsplit('.', 1)[0] + '.json'
                                                                temp = 'TEMP/' + file_name
                                                                write_json(res_info, temp)
                                                                if disk.upload(temp, file_name, adres):
                                                                    os.remove(temp)
                                                            else:
                                                                files_info_error += file_info
                                                        if len(files_info_error) != 0:
                                                            print('Следующие файлы не получилось сохранить:')
                                                            pprint(files_info_error)
                                                            files_info = files_info_error
                                                        else:
                                                            break
                                                        if not self.request_('\nПопробовать сохранить ещё раз(yes/no: '):
                                                            break
                                        print()
                                        return self.SaveFilesToDisk()

        return self.StartMenu('\nВозврат в стартовоеменю\n')


if __name__ == '__main__':
    # Получить путь к загружаемому файлу и токен от пользователя
    TOKEN_VK = read_file('tokens/token API_VK.txt')
    TOKEN_YN = read_file('tokens/token API_Yndex.txt')

    c = UserInterface()
    c.StartMenu()
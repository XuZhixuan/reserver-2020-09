import configparser
import requests
import pickle
import json
import re

from shutil import copyfile
from getpass import getpass

from reserve import load_runtime_data, get_campus, get_space_status
from login import login


def setup():
    print('Copying .env file')
    copyfile('.env.example', '.env')

    print('欢迎使用自动预约系统，下面将对项目进行基本配置')

    print('请配置账号信息:')
    username = input('Net-ID:')
    password = getpass('密码(No-Echo):')

    config = configparser.RawConfigParser()
    config.read('.env')
    config.set('login', 'username', username)
    config.set('login', 'password', password)

    with open('.env', 'w') as env:
        config.write(env)

    spaces = get_spaces()

    for space in spaces:
        priority = input('Priority of space ' + space.name + '=')
        space.priority = priority

    write_priority(spaces)
    write_seats(spaces)
    write_schedule()


def get_spaces():
    url = login()
    session = requests.Session()
    session.get(url)

    runtime_data = load_runtime_data(load_all=True)

    campus, cap_id = get_campus(session, runtime_data['campus'])
    print('Current campus chosen: ' + campus)

    return get_space_status(session, runtime_data['spaces_id'][cap_id])


def write_priority(spaces):
    data = pickle.dumps(spaces)

    with open('runtime/spaces.dat', 'wb') as bin_file:
        bin_file.write(data)


def write_seats(spaces):
    import json

    for i in range(len(spaces)):
        print('[%d]%s' % (i, spaces[i].name), end=' ')
    print('\n')

    prefer_seats = {}

    inputting = True

    while inputting:
        seats_string = input('输入您喜好的座位，按前后顺序空格隔开，格式为【空间:座位-座位】，如5:A112-A113-A114：')
        seats_groups = seats_string.split(' ')
        inputting = False
        for seats in seats_groups:
            temp = seats.split(':')
            index = int(temp[0])
            prefer_seats[spaces[index].identity] = temp[1].split('-')

            for seat in prefer_seats[spaces[index].identity]:
                if seat not in spaces[index].seats:
                    inputting = True
                    print('输入错误，%s 不在 %s 中' % (seat, spaces[index].name))

    with open('./runtime/prefer.json', 'w') as file:
        json.dump(prefer_seats, file)


def write_schedule():
    schedule = []
    time = '25:61'
    while not re.match(r'(2[0-3]|[01]?[1-9]):([0-5]?[0-9])', time):
        time = input('请输入每天运行脚本的时间（建议选择在06:00后运行）\n格式如："06:00" （无需双引号）:')
    schedule.append(time)

    with open('runtime/schedule.json', 'w') as file:
        json.dump(schedule, file)


def main():
    setup()

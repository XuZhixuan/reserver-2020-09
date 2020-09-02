from login import login
from login import http_build_query

import schedule
import requests
import time
import json
import re

from Space import Space


BASE_URL = 'http://rg.lib.xjtu.edu.cn:8086/'


def run(test=False):
    url = login()

    session = requests.Session()
    session.get(url)

    runtime_data = load_runtime_data()

    if not runtime_data['spaces']:
        campus, cap_id = get_campus(session, runtime_data['campus'])
        print('Current campus chosen: ' + campus)

        spaces = get_space_status(session, runtime_data['spaces_id'][cap_id])
    else:
        spaces = runtime_data['spaces']

    success = False
    for i in range(5):
        for space in spaces:
            space.update_status(session)
        seat, space = chose_seat(spaces, runtime_data['prefer'])
        reservation_code = send_reservation(space, seat, session)
        if not reservation_code:
            print('Reserve failed, retrying .....')
        else:
            print('预约成功，座位为%s-%s, 预约编号为%s' % (space, seat, reservation_code))
            success = True
            break

    if not success:
        print('[FAILED]Maximum retry times of 5 exceeded, exiting ...... ')
        return

    if test:
        cancel_reservation(session, reservation_code)


def get_campus(session, campus_list):
    url = BASE_URL + 'seat/'

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    print(' ..... done')

    campus = re.search(r'<span style="background:#AFEEEE">“(.*?)”</span>', response.text).group(1)

    campus_id = campus_list[campus]

    return campus, campus_id


def get_space_status(session, floors):
    spaces = []

    for floor, detail in floors.items():
        # noinspection SpellCheckingInspection
        url = BASE_URL + 'qspace?' + http_build_query({
            'floor': floor
        })

        print('[  OK  ]Requesting: ', url, end='')
        response = session.get(url)
        data = json.loads(response.text)
        print(' ..... done')

        for space_query in detail['spaces']:
            # noinspection SpellCheckingInspection
            space = Space(
                space_query,
                data['sp'][space_query],
                data['scount'][space_query][0],
                data['scount'][space_query][1]
            )
            spaces.append(space)

    for space in spaces:
        space.update_status(session)

    return spaces


def load_runtime_data(load_all=False):
    import os
    import json
    import pickle

    data = {}

    if os.path.exists('./runtime/prefer.json'):
        with open('./runtime/prefer.json', 'r') as json_file:
            data['prefer'] = json.load(json_file)
    else:
        data['prefer'] = None

    if os.path.exists('./runtime/spaces.dat'):
        with open('./runtime/spaces.dat', 'rb') as bin_file:
            data['spaces'] = pickle.load(bin_file)
        if not load_all:
            return data
    else:
        data['spaces'] = False

    runtime_files = [
        {'name': './runtime/spaces.json', 'mode': 'r', 'key': 'spaces_id'},
        {'name': './runtime/campus.json', 'mode': 'r', 'key': 'campus'}
    ]

    for file in runtime_files:
        with open(file['name'], file['mode']) as fp:
            datum = json.load(fp)
        data[file['key']] = datum

    return data


def chose_seat(spaces, prefer):
    import random

    if prefer:
        keys = [space.identity for space in spaces]
        objects = [space for space in spaces]
        spaces_dict = dict(zip(keys, objects))

        for prefer_space, prefer_seats in prefer.items():
            for seat in prefer_seats:
                if spaces_dict[prefer_space].seats[seat]:
                    return seat, prefer_space

    spaces = sorted(spaces, key=lambda x: x.priority, reverse=True)

    flag = False
    space = None

    for space in spaces:
        if space.available > 0:
            flag = True
            break

    if flag:
        seats = space.seats
        available_seats = []

        for seat, available in seats.items():
            if available:
                available_seats.append(seat)

        return random.choice(available_seats), space.identity
    else:
        print('当前无可用座位，停止运行')
        return False


def send_reservation(space, seat, session):
    url = BASE_URL + 'seat/?' + http_build_query({
        'kid': seat,
        'sp': space
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    print(' ..... done')

    try:
        data = re.search(r'cancelconfirm\(\'(.*?)\'\)', response.text).group(1)
    except AttributeError:
        print('预约失败')
        return False

    return data


def cancel_reservation(session, reservation_code):
    url = BASE_URL + 'my/?' + http_build_query({
        'cancel': '1',
        'ri': reservation_code
    })

    print('[  OK  ]Requesting: ', url, end='')
    response = session.get(url)
    print(' ..... done')


def load_schedules():
    import os

    if not os.path.exists('./runtime/schedule.json'):
        print('[FAILED]Schedules File Not Found, Please run setup tool to create one.')
        exit()

    with open('./runtime/schedule.json') as file:
        schedule_list = json.load(file)

    return schedule_list


def main():
    schedules = load_schedules()

    print('[  OK  ]Creating Scheduler', end='')
    for single_schedule in schedules:
        schedule.every().day.at(single_schedule).do(run)
    print(' ..... done')

    print('[  OK  ]Starting Scheduler ..... done')
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt as i:
            exit()
            print('[  OK  ]Exiting')

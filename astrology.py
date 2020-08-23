from collections import OrderedDict
from re import search as search
from bs4 import BeautifulSoup
from wikipediaapi import Wikipedia

import requests
import datetime
import peewee

db = peewee.SqliteDatabase("astrology.db")


class BaseTable(peewee.Model):
    class Meta:
        database = db


class Rich(BaseTable):
    name = peewee.CharField()
    bday = peewee.DateTimeField(null=True)
    zodiac = peewee.CharField(null=True)


def get_response(link):
    '''
    check site is alive
    '''
    response = requests.get(link)
    if response.status_code == 200:
        return response


def name_of_rich(link, how_much=2):
    '''
    Parsing the names of billionaires from the site Forbes.com
    '''
    global count
    if count != how_much:
        response = get_response(link)
        html_doc = BeautifulSoup(response.text, features='html.parser')
        name = only_name(html_doc.find('title').text)
        link = 'https://www.forbes.com' + html_doc.find('a', {'class': 'profile-nav__next'}).get('href')
        id_exist = True
        try:
            old_name = Rich.get(Rich.id == (count + 1))
        except Exception:
            id_exist = False
        if id_exist:
            if name != old_name.name:
                print(f'{old_name.name} change to {name}')
                old_name.name = name
                old_name.save()
        else:
            new_name = Rich.create(name=name)
        count += 1
        name_of_rich(link, how_much)


def find_zodiac(date):
    '''
    find the zodiac sign
    '''
    if (date.month == 12 and date.day >= 22) or (date.month == 1 and date.day <= 19):
        zodiac_sign = "Capricorn"
    elif (date.month == 1 and date.day >= 20) or (date.month == 2 and date.day <= 18):
        zodiac_sign = "Aquarium"
    elif (date.month == 2 and date.day >= 19) or (date.month == 3 and date.day <= 20):
        zodiac_sign = "Pices"
    elif (date.month == 3 and date.day >= 21) or (date.month == 4 and date.day <= 19):
        zodiac_sign = "Aries"
    elif (date.month == 4 and date.day >= 20) or (date.month == 5 and date.day <= 20):
        zodiac_sign = "Taurus"
    elif (date.month == 5 and date.day >= 21) or (date.month == 6 and date.day <= 20):
        zodiac_sign = "Gemini"
    elif (date.month == 6 and date.day >= 21) or (date.month == 7 and date.day <= 22):
        zodiac_sign = "Cancer"
    elif (date.month == 7 and date.day >= 23) or (date.month == 8 and date.day <= 22):
        zodiac_sign = "Leo"
    elif (date.month == 8 and date.day >= 23) or (date.month == 9 and date.day <= 22):
        zodiac_sign = "Virgo"
    elif (date.month == 9 and date.day >= 23) or (date.month == 10 and date.day <= 22):
        zodiac_sign = "Libra"
    elif (date.month == 10 and date.day >= 23) or (date.month == 11 and date.day <= 21):
        zodiac_sign = "Scorpio"
    elif (date.month == 11 and date.day >= 22) or (date.month == 12 and date.day <= 21):
        zodiac_sign = "Sagittarius"
    return zodiac_sign


def count_zodiC():
    """
    counting zodiac signs
    """
    count = {'Capricorn': 0,
             "Aquarium": 0,
             "Pices": 0,
             "Aries": 0,
             "Taurus": 0,
             "Gemini": 0,
             "Cancer": 0,
             "Leo": 0,
             "Virgo": 0,
             "Libra": 0,
             "Scorpio": 0,
             "Sagittarius": 0}
    for num in Rich.select():
        if num.zodiac is not None:
            count[num.zodiac] += 1
    return count


def birthday_of_rich(id=1):
    '''
    Parsing Billionaire Birthdays
    '''
    wiki = Wikipedia()
    for id in Rich.select().where(Rich.id >= id): #No data on the wikipedia site
        # print(id, id.name)
        no_bday = ['Qin Yinglin', 'Colin Zheng Huang', 'Zhong Huijuan', 'Walter P.J. Droege', 'Li Xiting',
                   'Yang Huiyan', 'Joseph Safra', 'Lukas Walton', 'Theo Albrecht, Jr.', 'Zhang Yiming', 'Lee Man Tat',
                   'Wang Wei', 'Radhakishan Damani', 'Liu Yonghao', 'Wu Yajun', 'Sun Piaoyang', 'Pang Kang',
                   'Udo Tschira', 'Xu Hang', 'Pallonji Mistry', 'Zhang Yong', 'Robert Ng', 'Iris Fontbona',
                   'Donald Newhouse', 'Graeme Hart', 'Goh Cheng Liang', 'Hank Meijer', 'Robin Zeng',
                   'Andreas Struengmann', 'Thomas Struengmann', 'Hui Wing Mau', 'Quek Leng Chan', 'Sun Hongbin',
                   'Zhang Bangxin', 'Lu Zhongfang', 'Cyrus Poonawalla', 'Scott Farquhar', 'Gong Hongjia',
                   'Eric Wittouck',
                   'Xu Shihui', 'Wang Wenyin', 'Zhang Fan', 'Chen Bang', 'Jiang Rensheng', 'Blair Parry-Okeden',
                   'David Duffield', 'Eyal Ofer', 'John Grayken']
        if id.name in no_bday:
            id.bday = datetime.datetime(1, 1, 1)
            id.save()
            continue
        page_py = wiki.page(id.name)
        link = page_py.fullurl
        response = get_response(link)
        html_doc = BeautifulSoup(response.text, features='html.parser')
        date = html_doc.find('span', {'class': 'bday'})
        if date is None:
            bday = fix_for_data(id.name)
        else:
            bday = datetime.datetime.strptime(date.text, '%Y-%m-%d')
        zodiac = find_zodiac(bday)
        id.bday = bday.date()
        id.zodiac = zodiac
        id.save()


def fix_for_data(name):
    """
    data not from wikipedia
    """
    if name == 'He Xiangjian':
        bday = datetime.datetime(1942, 10, 5)
    elif name == 'Thomas Peterffy':
        bday = datetime.datetime(1944, 9, 30)
    elif name == 'Heinz Hermann Thiele':
        bday = datetime.datetime(1941, 4, 2)
    elif name == 'Kwong Siu-hing':
        bday = datetime.datetime(1929, 12, 2)
    elif name == 'Lui Che Woo':
        bday = datetime.datetime(1929, 8, 9)
    elif name == 'Suleiman Kerimov':
        bday = datetime.datetime(1966, 3, 12)
    elif name == 'Joseph Tsai':
        bday = datetime.datetime(1964, 1, 1)
    elif name == 'Finn Rausing':
        bday = datetime.datetime(1955, 9, 1)
    elif name == 'Zong Qinghou':
        bday = datetime.datetime(1945, 10, 12)
    elif name == 'Carl Cook':
        bday = datetime.datetime(1962, 11, 10)
    elif name == 'Zhang Jindong':
        bday = datetime.datetime(1963, 3, 23)
    elif name == 'August von Finck':
        bday = datetime.datetime(1930, 3, 11)
    else:
        print(f'{name} don''t have data.')
    return bday


def only_name(name):
    """
    Making normal names
    """
    fix_name = ['David Thomson & family', 'John Mars', 'William Lei Ding', 'Jim Simons', 'Stefan Persson',
                'Hinduja brothers', 'Andrey Melnichenko', 'Ken Griffin', 'Udo & Harald Tschira', 'Robert & Philip Ng',
                'Hank & Doug Meijer', 'Stewart and Lynda Resnick', 'Anthony Pratt', 'Richard Qiangdong Liu',
                'Jim Kennedy', 'Stephen Ross', 'Thomas Frist, Jr. & family']
    if name in fix_name:
        new_fix_name = fix_for_wiki(name, fix_name)
        return new_fix_name
    match = search('&', name)
    if match is None:
        new_str = name
    else:
        new_str = name[0:match.start() - 1]
    return new_str


def fix_for_wiki(name, fix_name):
    """
    Fixing a name for wikipedia
    """
    if name == fix_name[0]:
        new_name = 'David Thomson, 3rd Baron Thomson of Fleet'
    elif name == fix_name[1]:
        new_name = 'John Franklyn Mars'
    elif name == fix_name[2]:
        new_name = 'Ding Lei'
    elif name == fix_name[3]:
        new_name = 'Jim Simons (mathematician)'
    elif name == fix_name[4]:
        new_name = 'Stefan Persson (magnate)'
    elif name == fix_name[5]:
        new_name = 'S. P. Hinduja'
    elif name == fix_name[6]:
        new_name = 'Andrey Melnichenko (industrialist)'
    elif name == fix_name[7]:
        new_name = 'Kenneth C. Griffin'
    elif name == fix_name[8]:
        new_name = 'Udo Tschira'
    elif name == fix_name[9]:
        new_name = 'Robert Ng'
    elif name == fix_name[10]:
        new_name = 'Hank Meijer'
    elif name == fix_name[11]:
        new_name = 'Stewart Resnick'
    elif name == fix_name[12]:
        new_name = 'Anthony Pratt (businessman)'
    elif name == fix_name[13]:
        new_name = 'Liu Qiangdong'
    elif name == fix_name[14]:
        new_name = 'James C. Kennedy'
    elif name == fix_name[15]:
        new_name = 'Stephen M. Ross'
    elif name == fix_name[16]:
        new_name = 'Thomas F. Frist Jr.'
    return new_name


Rich.create_table()
rich = {}
count = 0
answer = input('Update list from Forbes.com?(y/n):')
if answer == 'y':
    start_link = 'https://www.forbes.com/profile/jeff-bezos/?list=billionaires#436b8bac1b23'
    print(f"Start finding names of billionaires on site Forbes.com")
    name_of_rich(link=start_link, how_much=200)
answer = input('Update list from Wikipedia.com?(y/n):')
if answer == 'y':
    print(f"Start finding birthday of billionaires on site wikipedia.com")
    birthday_of_rich()

zodiac_count = count_zodiC()
zodiac_count_sorted = OrderedDict(sorted(zodiac_count.items(), key=lambda x: x[1]))
print('zodiac signs descending:')
for i, (zod, count) in enumerate(reversed(zodiac_count_sorted.items())):
    print(f'{i + 1} - {zod} under the zodiac sign {count} billionaires')

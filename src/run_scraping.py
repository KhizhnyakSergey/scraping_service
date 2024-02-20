import codecs
import os, sys

from django.db import DatabaseError
from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping_service.settings"

import django
django.setup()

from scraping.parsers import *
from scraping.models import (
    Vacancy, 
    City, 
    Language, 
    Error, 
    Url
)

User = get_user_model()

parsers = (
    (work, 'https://www.work.ua/ru/jobs-kyiv-python/'),
    (dou, 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D1%97%D0%B2&search=python'),
    (djinni, 'https://djinni.co/jobs/?primary_keyword=Python&region=UKR&location=kyiv'),
    (rabota, 'https://robota.ua/zapros/python/kyiv'),
)

def get_settings():
    qs = User.objects.filter(send_email=True).values()
    settings_data_set = set((q['city_id'], q['language_id']) for q in qs)
    return settings_data_set

def get_urls(_settings): # list tuples
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        tmp = {}
        tmp['city'] = pair[0]
        tmp['language'] = pair[1]
        tmp['url_data'] = url_dict[pair]
        urls.append(tmp)
    return urls

q = get_settings()
u = get_urls(q)

city = City.objects.filter(slug='kiev').first()
language = Language.objects.filter(slug='python').first()


jobs, errors = [], []

for func, url in parsers:
    j, e = func(url)
    jobs += j
    errors += e

for job in jobs:
    print(job)
    v = Vacancy(**job, city=city, language=language)
    try:
        v.save()
        print("Data saved successfully!")
    except DatabaseError as e:
        print("Error saving data:", e)
if errors:
    er = Error(data=errors).save()

# h = codecs.open('work.txt', 'w', encoding='utf-8')
# h.write(str(jobs))
# h.close()
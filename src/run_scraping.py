import codecs
import asyncio
import os, sys
import datetime as dt

from django.db import DatabaseError, IntegrityError
from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping_service.settings"

import django
django.setup()

from scraping.parsers import *
from scraping.models import (
    Vacancy, 
    Error, 
    Url
)

User = get_user_model()

parsers = (
    (work, 'work'),
    (dou, 'dou'),
    (djinni, 'djinni'),
    (rabota, 'rabota')
)

jobs, errors = [], []

def get_settings():
    qs = User.objects.filter(send_email=True).values()
    settings_data_set = set((q['city_id'], q['language_id']) for q in qs)
    return settings_data_set

def get_urls(_settings): # list tuples
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        if pair in url_dict:
            tmp = {}
            tmp['city'] = pair[0]
            tmp['language'] = pair[1]
            url_data = url_dict.get(pair)
            if url_data:
                tmp['url_data'] = url_dict.get(pair)
                urls.append(tmp)
    return urls

async def main(value):
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language) 
    errors.extend(err)
    jobs.extend(job)


settings = get_settings()
url_list = get_urls(settings)


# loop = asyncio.get_event_loop()
# Создаем новый цикл событий
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tmp_tasks = [(func, data['url_data'][key], data['city'], data['language'])
             for data in url_list
             for func, key in parsers]

tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])
loop.run_until_complete(tasks)
loop.close()  

# for data in url_list:

#     for func, key in parsers:
#         url = data['url_data'][key]
#         j, e = func(url, city=data['city'], language=data['language'])
#         jobs += j
#         errors += e

     
for job in jobs:
    v = Vacancy(**job)
    try:
        v.save()
        print("Data saved successfully!")
    except IntegrityError as un:
        print('dublicate', v.url)
    except DatabaseError as e:
        print("Error saving data:", e)
if errors:
    qs = Error.objects.filter(timestamp=dt.date.today())
    if qs.exists():
        # err = qs.first()
        # err.data.update({'errors1': errors})
        # err.save()
        err = qs.first()
        err_data = err.data  # Assuming err.data is a dictionary
        err_data['errors'] = errors  # Assuming errors is a list
        err.save()
    else:
        er = Error(data=f'errors:{errors}').save()

# h = codecs.open('work.txt', 'w', encoding='utf-8')
# h.write(str(jobs))
# h.close()
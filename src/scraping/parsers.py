import requests
import codecs
from random import randint 

from bs4 import BeautifulSoup as BS



__all__ = ('work', 'rabota', 'dou', 'djinni')


headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;p=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;p=0.8'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;p=0.8'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;p=0.8'}
           ]

def work(url: str):

    jobs = []
    errors = []

    domain = 'https://www.work.ua'
    url = 'https://www.work.ua/ru/jobs-kyiv-python/'
    resp = requests.get(url, headers=headers[randint(0, 3)])

    if resp.status_code == 200:
        soup = BS(resp.content, 'html.parser')
        main_div = soup.find('div', id='pjax-job-list')
        if main_div:
            div_list = main_div.find_all('div', attrs={'class': 'job-link'})
            for div in div_list:
                title = div.find('h2')
                href =  title.a['href']
                description = div.p.text
                company = div.find('div', attrs={'class': 'add-top-xs'})
                if company:
                    # span_company = company.find('span').get_text()
                    company_name = company.span.text
                jobs.append({'title': title.text,
                            'url': domain + href,
                            'company': company_name,
                            'description': description
                            })
        else:
            errors.append({'url': url, 'title': 'div does not exists'})
    else:
        errors.append({'url': url, 'title': 'Page not response'})

    return jobs, errors


def rabota(keywords: str = None, cityId: int = None):

    jobs = []
    errors = []

    headers = {
    'authority': 'dracula.robota.ua',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    params = {
        'q': 'getPublishedVacanciesList',
    }

    json_data = {
        'operationName': 'getPublishedVacanciesList',
        'variables': {
            'pagination': {
                'count': 1000,
                'page': 0,
            },
            'filter': {
                'keywords': 'python',
                'clusterKeywords': [],
                'cityId': '1',
                'salary': 0,
                'districtIds': [],
                'scheduleIds': [],
                'rubrics': [],
                'metroBranches': [],
                'showAgencies': True,
                'showOnlyNoCvApplyVacancies': False,
                'showOnlySpecialNeeds': False,
                'showOnlyWithoutExperience': False,
                'showOnlyNotViewed': False,
                'showWithoutSalary': True,
            },
            'sort': 'BY_VIEWED',
        },
        'query': 'query getPublishedVacanciesList($filter: PublishedVacanciesFilterInput!, $pagination: PublishedVacanciesPaginationInput!, $sort: PublishedVacanciesSortType!) {\n  publishedVacancies(filter: $filter, pagination: $pagination, sort: $sort) {\n    totalCount\n    items {\n      ...PublishedVacanciesItem\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PublishedVacanciesItem on Vacancy {\n  id\n  schedules {\n    id\n    __typename\n  }\n  title\n  description\n  sortDateText\n  hot\n  designBannerUrl\n  isPublicationInAllCities\n  badges {\n    name\n    __typename\n  }\n  salary {\n    amount\n    comment\n    amountFrom\n    amountTo\n    __typename\n  }\n  company {\n    id\n    logoUrl\n    name\n    __typename\n  }\n  city {\n    id\n    name\n    __typename\n  }\n  showProfile\n  seekerFavorite {\n    isFavorite\n    __typename\n  }\n  seekerDisliked {\n    isDisliked\n    __typename\n  }\n  formApplyCustomUrl\n  anonymous\n  isActive\n  publicationType\n  __typename\n}\n',
    }

    response = requests.post('https://dracula.robota.ua/', params=params, headers=headers, json=json_data)

    if response.status_code == 200:
        data = response.json()

        # Получаем список вакансий
        vacancies = data.get('data', {}).get('publishedVacancies', {}).get('items', [])

        # Проходимся по каждой вакансии и добавляем нужные данные в список jobs
        for vacancy in vacancies:

            id = vacancy.get('id', '')
            company_id = vacancy.get('company').get('id')
            title = vacancy.get('title', '')
            company = vacancy.get('company').get('name')
            description = vacancy.get('description', '')
            description_cleaned = description.replace('\xa0', '').replace('\r', '').replace('\n', '').replace('\t', '')
            href = f'https://robota.ua/company{company_id}/vacancy{id}',

            jobs.append({'title': title,
                        'url': href,
                        'company': company,
                        'description': description_cleaned
                        })
    else:
        errors.append(f"Error {response.status_code}: {response.text}")
    
    return jobs, errors


def dou(url: str):

    jobs = []
    errors = []

    resp = requests.get(url, headers=headers[randint(0, 3)])

    if resp.status_code == 200:
        soup = BS(resp.content, 'html.parser')
        main_div = soup.find('div', id='vacancyListId')
        if main_div:
            li_list = main_div.find_all('li', attrs={'class': 'l-vacancy'})
            for li in li_list:
                if '__hot' not in li['class']:
                    title = li.find('div', attrs={'class': 'title'})
                    href =  title.a['href']
                    description = li.find('div', attrs={'class': 'sh-info'})
                    description_text = description.text
                    company = title.find('a', attrs={'class': 'company'})
                    if company:
                        company_name = company.text.strip()
                    jobs.append({'title': title.text,
                                'url': href,
                                'company': company_name,
                                'description': description_text
                                })
        else:
            errors.append({'url': url, 'title': 'div does not exists'})
    else:
        errors.append({'url': url, 'title': 'Page not response'})

    return jobs, errors

def djinni(url: str):

    jobs = []
    errors = []
    domain = 'https://djinni.co'
    resp = requests.get(url, headers=headers[randint(0, 3)])

    if resp.status_code == 200:
        soup = BS(resp.content, 'html.parser')
        main_ul = soup.find('ul', attrs={'class': 'list-jobs'})
        if main_ul:
            li_list = main_ul.find_all('li', attrs={'class': 'list-jobs__item'})
            for li in li_list:
                title = li.find('a', attrs={'class': 'job-list-item__link'})
                href =  title['href']
                description = li.find('div', attrs={'class': 'job-list-item__description'})
                description_text = description.text
                company = li.find('a', attrs={'class': 'mr-2'})
                if company:
                    company_name = company.text
                jobs.append({'title': title.text.replace('\n', '').strip(),
                            'url': domain + href,
                            'company': company_name.replace('\n', '').strip(),
                            'description': description_text.replace('\n', '').replace('Детальніше', '').strip()
                            })
        else:
            errors.append({'url': url, 'title': 'div does not exists'})
    else:
        errors.append({'url': url, 'title': 'Page not response'})

    return jobs, errors


if __name__ == '__main__':
    # url = 'https://robota.ua/zapros/python/kyiv'
    # jobs, errors = rabota(url)    
    # x = rabota()    
    # print(x)

    # url = 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D1%97%D0%B2&search=python'

    url = 'https://djinni.co/jobs/?primary_keyword=Python&region=UKR&location=kyiv'
    
    jobs, errors = djinni(url) 
    h = codecs.open('work.text', 'w', encoding='utf-8')
    h.write(str(jobs))
    h.close()


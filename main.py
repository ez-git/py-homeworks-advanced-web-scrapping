import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

search_link = 'https://spb.hh.ru/search/vacancy?text=NAME%3A%28python%29' \
              '+and+DESCRIPTION%3A%28Django+OR+Flask%29&area=1&area=2'
headers = {'User-Agent': UserAgent().chrome}
ret = requests.get(search_link, headers=headers)
soup = BeautifulSoup(ret.text, 'html.parser')

data = []
vacancies = soup.find_all('div', class_='vacancy-serp-item-body__main-info')

for vacancy in vacancies:
    link = vacancy.find('a', class_='serp-item__title').attrs.get('href')

    salary_from = ''
    salary_to = ''
    currency = ''
    salary = vacancy.find_all('span', class_='bloko-header-section-3')
    whitespace_code = '\u202f'
    if len(salary) != 0:
        current_salary = salary[0].contents
        if len(current_salary) == 7:
            if current_salary[0] == 'от':
                if current_salary[2] != ' ':
                    salary_from = int(
                        current_salary[2].replace(whitespace_code, ''))
            else:
                if current_salary[2] != ' ':
                    salary_to = int(
                        current_salary[2].replace(whitespace_code, ''))
            currency = current_salary[6]
        elif len(current_salary) == 3:
            if current_salary[0] != ' ':
                salary_from_to = current_salary[0].split(' – ')
                salary_from = int(
                    salary_from_to[0].replace(whitespace_code, ''))
                salary_to = int(salary_from_to[1].replace(whitespace_code, ''))
                currency = current_salary[2]

    if currency != 'USD':
        continue

    company_name_list = \
        vacancy.find_all('a', class_='bloko-link bloko-link_kind-tertiary')[
            0].contents

    if len(company_name_list) == 1:
        company = company_name_list[0]
    else:
        company = company_name_list[0] + company_name_list[2]
    company = company.replace(' ', ' ')

    city = vacancy.find_all('div', class_='bloko-text', attrs={
        'data-qa': 'vacancy-serp__vacancy-address'})[0].contents[0]

    data.append({
        'link': link,
        'salary_from': salary_from,
        'salary_to': salary_to,
        'currency': currency,
        'company': company,
        'city': city
    })

    with open('vacancies.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

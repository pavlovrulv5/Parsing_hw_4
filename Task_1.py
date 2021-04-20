from pprint import pprint
import requests
from lxml import html
import datetime
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}


def requests_lenta_news():
    url = 'https://lenta.ru' #тут понятно сайт беру
    response = requests.get(f'{url}', headers=headers) #респонс и т.д.
    shit = html.fromstring(response.text)
    parsing_novostey = shit.xpath("//div[contains(@class,'b-yellow-box__wrap')]/div[contains(@class, 'item')]")
    govno_news = [] #складываю в коллекцию ссылку через div(новости где справа), т.к. хз,можно через сэкшн, но пох..
    #и так работает
    for item in parsing_novostey: #по циклу получаю тайтл новости, ссылку на новости и т.д.
        news = {}
        name_source = 'lenta.ru'
        name_news = item.xpath(".//a/text()")
        link_news_info = item.xpath(".//a/@href")
        link_news = f'{url}{link_news_info[0]}'
        response_2 = requests.get(link_news, headers=headers)
        shit = html.fromstring(response_2.text)
        sranye_novosti = shit.xpath(".//div[@class = 'b-topic__info']/time/@datetime")
        date_news = sranye_novosti[0][:10].split('-')
        date_news = datetime.date(int(date_news[0]), int(date_news[1]), int(date_news[2])).strftime('%d.%m.%Y')
        news['name_source'] = name_source
        news['name_news'] = name_news[0].replace(u'\xa0', ' ')
        news['link_news'] = link_news
        news['date_news'] = date_news

        govno_news.append(news)

    return govno_news


def requests_yandex_news(): #не фонтан lxml возможностей...но вроде работает
    url = 'https://yandex.ru/news'
    response = requests.get(f'{url}', headers=headers)
    shit = html.fromstring(response.text)
    parsing_novostey = shit.xpath("//article[contains(@class,'mg-card')]//a[contains(@href,'rubric=science') and @class='mg-card__link']/ancestor::article")
    govno_news = []
    for item in parsing_novostey:
        news = {}
        name_source = item.xpath(".//span[contains(@class, 'mg-card-source__source')]//text()")
        name_news = item.xpath(".//div[contains(@class, 'mg-card__text')]//h2/text()")
        link_news = item.xpath(".//div[contains(@class, 'mg-card__text')]/a/@href")
        sranye_novosti = item.xpath(".//span[contains(@class, 'mg-card-source__time')]/text()")

        try:
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
            sranye_novosti = sranye_novosti.replace('Вчера', yesterday)
        except AttributeError:
            today = datetime.date.today().strftime('%d.%m.%Y')
            sranye_novosti = f'{today} {sranye_novosti[0]}'

        news['name_source'] = name_source[0]
        news['name_news'] = name_news[0]
        news['link_news'] = link_news[0]
        news['date_news'] = sranye_novosti
        govno_news.append(news)

    return govno_news


def requests_mail_news():
    url = 'https://news.mail.ru/'
    response = requests.get(f'{url}', headers=headers)
    shit = html.fromstring(response.text)
    parsing_novostey= shit.xpath("//div[contains(@class,'daynews__')]/a | //ul[@data-module='TrackBlocks']/li[@class='list__item']/a")
    govno_news = []

    for i, item in enumerate(parsing_novostey, 1):
        news = {}
        if i < 6:
            name_news = item.xpath(".//span[contains(@class, 'photo__title')]/text()")
        else:
            name_news = item.xpath(".//text()")
        link_news = item.xpath(".//@href")
        response_2 = requests.get(link_news[0], headers=headers) #делаю доп. запрос
        dom = html.fromstring(response_2.text) #для инфо по новости
        name_source = dom.xpath("//span[contains(@class, 'breadcrumbs__item')]//a//text()")
        sranye_novosti = dom.xpath("//span[contains(@class, 'breadcrumbs__item')]//span[contains(@class, 'note__text')]/@datetime")
        date_news = sranye_novosti[0][:10].split('-')
        date_news = datetime.date(int(date_news[0]), int(date_news[1]), int(date_news[2])).strftime('%d.%m.%Y')
        news['name_source'] = name_source[0]
        news['name_news'] = name_news[0].replace(u'\xa0', ' ')
        news['link_news'] = link_news[0]
        news['date_news'] = date_news
        govno_news.append(news)

    return govno_news


if __name__ == "__main__":
    lenta_news = requests_lenta_news()
    pprint(lenta_news)
    yandex_news = requests_yandex_news()
    pprint(yandex_news)
    mail_news = requests_mail_news()
    pprint(mail_news)
    client = MongoClient('localhost', 27017)
    db = client['News']
    news = db.news
    news.insert_many(lenta_news)
    news.insert_many(yandex_news)
    news.insert_many(mail_news)

# Нихера не понятно как от /xa избавиться
from bs4 import BeautifulSoup
import requests
import re

URL = input('Введите ссылку для запроса цены: ')
# URL = 'https://www.forever21.com/us/2000449071.html?dwvar_2000449071_color=01&dwvar_2000449071_size=2&quantity=1'
# URL = 'https://www.forever21.com/us/2000453109.html?dwvar_2000453109_color=02&dwvar_2000453109_size=4&quantity=1'
# URL = 'https://aliexpress.ru/item/1005001551150863.html?_ga=2.59516461.1649609693.1641585631-1047473145.1639031512&_gac=1.86857194.1641485363.Cj0KCQiAw9qOBhC-ARIsAG-rdn5JIDnZQOQFWk1R8o3XNp2gYBnZwnH58IeOQ-BnshcK_spbnhzBpvwaAlqBEALw_wcB&gps-id=5589723&item_id=1005001551150863&pdp_ext_f=%7B%22sku_id%22%3A%2212000026593401751%22%2C%22ship_from%22%3A%22CN%22%7D&pvid=3a12eccf-0aed-444e-a654-ef36f1fa4659&scm=1007.23880.125255.0&scm-url=1007.23880.125255.0&scm_id=1007.23880.125255.0&sku_id=12000021756507555&spm=a2g01.12602323.fdpcl001.3.6d15753fc1HMXs'
# URL = 'https://www.ebay.com/itm/234368110682?hash=item36916d905a:g:VQQAAOSwER1h2RVH'
# URL = 'https://www.amazon.com/SENZER-SG500-Surround-Cancelling-Microphone/dp/B08FX35S7K/ref=sr_1_1_sspa?keywords=gaming+headsets&pd_rd_r=6bff59d5-a96c-4986-976c-0b0251d1782b&pd_rd_w=VCsFV&pd_rd_wg=keg2T&pf_rd_p=12129333-2117-4490-9c17-6d31baf0582a&pf_rd_r=EMTFK7VKS588867YNCP5&qid=1641669120&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUFDNTBRWFhaVU5JS0smZW5jcnlwdGVkSWQ9QTA3MzQ2ODkyODdIRERMTTY4R05PJmVuY3J5cHRlZEFkSWQ9QTA0MDg4MjY1V0Q1QUpFQURVUVkmd2lkZ2V0TmFtZT1zcF9hdGYmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl'
# URL = 'https://detail.tmall.com/item.htm?spm=875.7931836.0.0.5ea34265HunzYa&scm=1007.12710.81708.110&id=617718312163&pvid=fc7d9ba6-75ae-4f6b-a45b-24523b83b492&skuId=4972900674017'

#Введите процент наценки
INTEREST = 0.2

#Разбивка ссылки для проверки
url_split = URL.split('/')[2]

#Функция запроса страницы
def get_soup(url):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'close',
    }

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup

#Функция обработки цен
def get_price(soup, interest):
    url_type = URL.split('/')[2]
    if url_type == 'www.forever21.com':
        price = float(soup.find(class_='price').find_all(class_='value')[1].text.replace(',', '').replace('RUB', ''))
        print(type(price))
        end_price = f'{(price) * (1 + interest)} RUB'

    elif url_type == 'aliexpress.ru':
        # print(soup)
        price = float(soup.find('span', 'Product_UniformBanner__uniformBannerBoxPrice__o5qwb').text.replace('US $', ''))
        end_price = f'$ {(float(price) * (1 + interest))}'

    elif url_type == 'detail.tmall.com':
        price = soup.select('script')
        scripts = price
        skuid = URL.split('skuId=')[1]

        for n, str in enumerate(price):
            if 'price' in str:
                price = str.find('price')

        result = ''

        price = []
        scripts = [script for script in scripts]
        for script in scripts:
            if 'price' and skuid in script.text:
                result = script
                price = re.split(r'"price"', (script.text))

        found_price = ''
        for n, i in enumerate(price):
            if skuid in i:
                found_price = (i.split(',')[0]).replace('"', '').replace(':', '')

        end_price = (float(found_price) * (1 + interest))

    elif url_type == 'www.ebay.com':
        price = float(soup.find(class_='val').find('span', class_='notranslate').text.replace('US $', '').replace(',', '.'))
        delivery = soup.find(id='shippingSummary').find('span', id='fshippingCost').find('span').text.replace('US $', '').replace(',', '.')
        if delivery != 'БЕСПЛАТНО':
            delivery = float(delivery)
        else:
            delivery = 0
        end_price = f'${(price * (1 + interest)) + delivery}'

    elif url_type == 'www.amazon.com':
        price = float(soup.find(class_='a-box-inner').find('span', id='price_inside_buybox').text.strip().replace('$', ''))
        delivery = float(soup.find(class_='a-box-inner').find_all('span', class_='a-size-base')[6].text.strip().replace('$', ''))
        end_price = f'$ {(price * (1 + interest) + delivery)}'
    else:
        end_price = 'Сайт не поддерживается'

    return  end_price

def main():
    soup = get_soup(URL)
    price = get_price(soup, INTEREST)
    print(f'Ваша цена составляет: {price}')

if __name__ == '__main__':
    main()
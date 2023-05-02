#!/usr/bin/python3
import requests
import bs4
import re
import SQLHandler
import threading
import time
import logging

logger = logging.getLogger('error_logger')
logger.setLevel(logging.INFO)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_file_handler = logging.FileHandler('/var/log/pricetracker_info_crawler.log')
error_file_handler.setFormatter(error_formatter)
logger.addHandler(error_file_handler)


logger_update = logging.getLogger('info_logger')
logger_update.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/pricetracker_info_updater.log')
file_handler.setFormatter(error_formatter)
logger_update.addHandler(file_handler)

def get_token(code):
    response = requests.get(f'https://pricehistory.app/p/{code}')
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    alltags = soup.find_all('script')
    tags = alltags[5]
    tags = tags.text.strip()
    token = re.search(r'(?<=token", ")[a-z0-9]+', tags).group()
    print(token)
    return token

def price_data(link):
    headers = {
        'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://pricehistory.app/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0',
        'Content-Type': 'application/json',
    }

    json_data = {
        'url': link,
    }

    response = requests.post('https://pricehistory.app/api/search', headers=headers, json=json_data)
    #print("response.content--------", response.content)
    statuscode = response.status_code
    
    try:
        code = response.json()["code"]
        print(code)
        response = requests.get(f'https://pricehistory.app/p/{code}')
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        #mrp = soup.find('table', {"class":"ph-table-offer"}).find('tr').find_next_sibling('tr').find_next_sibling('tr').find('td').text.strip()
        price = soup.find('table', {"class":"ph-table-offer"}).find('td').text.strip()
        lowest_price = soup.find('table', {"class":"ph-table-overview"}).find('td', {'class':'text-success'}).text.strip()
        average_price = soup.find('table', {"class":"ph-table-overview"}).find('td', {'class':'text-primary'}).text.strip()
        highest_price = soup.find('table', {"class":"ph-table-overview"}).find('td', {'class':'text-danger'}).text.strip()
        name = soup.find('h1').text.strip()
        price_int = int(re.sub('[^0-9]', '', price))

        #mrp_int = int(re.sub('[^0-9]', '', mrp))
        data = {}
        data["name"] = name
        data['prices'] = {}
        data["prices"]["price"] = price_int
        #data["prices"]["mrp"] = mrp_int
        data["prices"]["highest_price"] = highest_price
        data["prices"]["average_price"] = average_price
        data["prices"]["lowest_price"] = lowest_price
        
        print("price_data--------", data)
        return data, code, statuscode
    except:
        return None

def crawler(link):
    try:
        response = price_data(link)
        print(response)
        #print("crawler-----status_code--------",response[2])
        #print("crawler ---------code--------", response[1])
        id = re.search(r'(?<=-)\w+(?=$)', str(response[1])).group()
        print("id-----------", id)
        headers = {
            'authority': 'pricehistory.app',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            # 'cookie': 'google-analytics_v4_84af__ga4sid=703614115; google-analytics_v4_84af__session_counter=1; google-analytics_v4_84af__ga4=573da3ff-7e40-4c4c-a9f0-27348e304ba0; google-analytics_v4_84af___z_ga_audiences=573da3ff-7e40-4c4c-a9f0-27348e304ba0; cf_zaraz_google-analytics_7ab2=true; cf_zaraz_google-analytics_v4_84af=true; google-analytics_7ab2___ga=e00f5a7e-a2ab-4a09-a757-cc49b8d602ff; google-analytics_v4_84af__engagementPaused=1682230859723; google-analytics_v4_84af__engagementStart=1682230861180; google-analytics_v4_84af__counter=18; google-analytics_v4_84af__let=1682230861180',
            'origin': 'https://pricehistory.app',
            'page': f'{id}',
            'referer': 'https://pricehistory.app/p/leader-buddy-16t-sea-green-light-pink-jGj3x3Q2',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'token': get_token(response[1]),
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        }
        json_data = {}

        response1 = requests.post(f'https://pricehistory.app/api/report/refresh/{id}', headers=headers, json=json_data)
        print("crawler------------", response1.content)
        logger.info(response1.content)
        #print(response)
        return response
    except Exception as e:
        print(e)
def price_updater(link):
    crawler(link)
    time.sleep(4)
    #print(f"link--------{link}")
    try:
        return price_data(link)[0]
    except TypeError as e:
        print('kindly try after some time')
def actual_updater():
    list = SQLHandler.get_product_list()
    for i in list:
        print(i)
        if i[0] == 'Amazon':
            #print('amazon')
            link = f'https://www.amazon.in/dp/{i[1]}?tag=b2bdeals-21'
            print("link------", link)
            data = price_updater(link)
            if data != None:
                price = data['prices']['price']
                low_price = data['prices']['lowest_price']
                avg_price = data['prices']['average_price']
                high_price = data['prices']['highest_price']
                print (price, "      latest vs DB price      ", i[4])
                if price != i[4] or str(low_price) != i[5] or str(high_price) != i[6] or str(avg_price) != i[7]:    #BUG price was not a string in DB
                    try:
                        SQLHandler.update_product_list_amazon(i[1], price, low_price, high_price, avg_price)
                        logger_update.info(f'Current Price in DB was {i[4]} and the price got from crawler is {price}')
                        print(i[4], '                       -------------------------- Current Price in DB, price got from crawler---------------', price)
                        #print('updated')
                    except:
                        logger_update.error(f'Wasn\'t able to update database. -- ProductID: {i[1]}')
                else:
                    print('same')
                    return True 
            else:
                logger_update.error(f'data is none, website--- {i[0]}')
        elif i[0] == 'Flipkart':
            logger_update.info('reached flipkart elif')
            link = f'https://www.flipkart.com/{i[3]}/p/{i[2]}'
            data = price_updater(link)
            if data != None:
                if price != i[4] or str(low_price) != i[5] or str(high_price) != i[6] or str(avg_price) != i[7]:
                    try:
                        logger_update.info(f'reached sql function flipkart updater with current price of {price} and prev price if {i[4]}')
                        SQLHandler.update_product_list_flipkart(i[2], price, low_price, high_price, avg_price) 
                    except:
                        logger_update.error(f'Wasn\'t able to update database. ProductID: {i[2]}, Product Slug: {i[3]}')
                    #print('updated now fk')
                else:
                    logger_update.info('data seems same')
                    logger_update.info(f'DATA ----- {data} \n\n Data from DB: {i}')
                #return True
            else:
                logger_update.error(f'data is none, website--- {i[0]}')
                
def threader():
    while True:
        print('actual updater')
        actual_updater()
        time.sleep(100)
thread = threading.Thread(target=threader)
#thread.daemon = True
thread.start()
#print(price_data("https://www.flipkart.com/"))
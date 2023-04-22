import requests
import bs4
import re, time
import SQLHandler 
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
    print("response.content--------", response.content)
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
        return data
    except:
        return None

#price_data("https://www.amazon.in/dp/B0B77D296W?tag=coa_in_g-21")

def crawler(link):
    try:
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
        print("crawler-----",response.status_code)
        code = response.json()["code"]
        print("crawler ---------", code)
        id = re.search(r'(?<=-)\w+(?=$)', code).group()
        print("id-----------", id)

        headers = {
            'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
            'page': 'Adozghce',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            'Referer': 'https://pricehistory.app/p/redmi-watch-2-lite-muli-system-standalone-Adozghce',
            'token': '5c37d9b78d43d39cbf52e8b3bf72afd670bdcc5dd1049171049291f84b4d58f2',
            'sec-ch-ua-platform': '"Android"',
        }
        json_data = {}

        response = requests.post(f'https://pricehistory.app/api/report/refresh/{id}', headers=headers, json=json_data)
        print("crawler------------", response.content)
    except Exception as e:
        print(e)
def price_updater(link):
    crawler(link)
    #time.sleep(2)
    return price_data(link)


def actual_updater():
    list = SQLHandler.get_product_list()
    for i in list:
        print(i)
        if i[0] == 'Amazon':
            print('amazon')
            link = f'https://www.amazon.in/dp/{i[1]}'
            print("link------", link)
            data = price_updater(link)
            if data != None:
                print (data['prices']['price'], "            ", i[4]) 
                if str(data['prices']['price']) == str(i[4]):
                    print('same')
                else:
                    print('update now')
                    SQLHandler.update_product_list_amazon(i[1], data['prices']['price'])
        elif i[0] == 'Flipkart':
            print('flipkart')
            link = f'https://www.flipkart.com/{i[3]}/p/{i[2]}'
            data = price_updater(link)
            if data != None:
                if str(data['prices']['price']) == str(i[4]):
                    print('same')
                else:
                    print('update now fk')
                    SQLHandler.update_product_list_flipkart(i[2], data['prices']['price']) 
actual_updater()
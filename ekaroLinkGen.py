#!/usr/bin/python3
import requests
import bs4
import re
def create_link(link):
    cookies = {
        'RID': '2689901',
        'customerType': 'new',
        'pps_referance_cookie_e4adec0a3856cae8c9d623a3ee12d9ab': 'e9427c7da1771a3f904a051961a92fe4%2C1687195381%2C1682012281%2Ca67b0956620d2e2f35749bc23936c6f2',
        'jofedate': 'MDQvMjYvMjAyMyAwODozMToyOQ%3D%3D',
        'X-PPS-Status': 'signed',
    }

    headers = {
        'authority': 'earnkaro.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': 'RID=2689901; customerType=new; pps_referance_cookie_e4adec0a3856cae8c9d623a3ee12d9ab=7a4c24b1ebc9c0989bb54fa05b3f45e2%2C1687079517%2C1681896417%2C06e6f73f98768751333526f413ef64c2; jofedate=MDQvMjYvMjAyMyAwODozMToyOQ%3D%3D; X-PPS-Status=signed',
        'origin': 'https://earnkaro.com',
        'referer': 'https://earnkaro.com/create-earn-link',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
    }

    data = {
        'deallink': link,
        'responseMsg': '',
    }

    response = requests.post('https://earnkaro.com/create-earn-link', cookies=cookies, headers=headers, data=data)
    print(response.content)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    try:
        shortlink = soup.find('input', {'id':'deallinkshorturl'})['value']
        print(shortlink)
        return shortlink
    except TypeError as tperror:
        print('Ekaro Link Not Generated. NoneType Error.')
        return None
import requests
import re
from bs4 import BeautifulSoup
def get_tok():
    tok = requests.get('https://www.wheregoes.com')
    token = re.search(r'(?<=\")[a-zA-Z0-9=]+(?=\" style=\"display:none;)', str(tok.text)).group()
    print(f"wheregoes token ----{token}")
    return token

def wheregoes(link):
    headers = {
        'authority': 'wheregoes.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://wheregoes.com',
        'referer': 'https://wheregoes.com/',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0',
    }

    data = {
        'url': str(link),
        'ua': 'Wheregoes.com Redirect Checker/1.0',
        'phn': '',
        'php': get_tok(),
    }

    response = requests.post('https://wheregoes.com/trace/', headers=headers, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    main_link_element = soup.select('a[href^="https://www."]')
    try:
        main_link = main_link_element[0]['href']
        url = main_link
        if url.startswith("https://www.amazon.in/"):
            product_id = re.search(r'(?<=p/)([^/?]+)', url).group()
            print(product_id)
            return product_id
        elif url.startswith("https://www.flipkart"):
            print(url)
            fkpid = re.search(r'(?<=p/)[^?]+', url).group()
            fkslug = re.search(r'(?<=com/)[^/]+', url).group()
            print(fkpid)
            print(fkslug)
            return fkpid, fkslug
        else:
            print("wheregoes unable")
            return None
    except:
        print(f"It is not an AMAZON link.")
        return None

def message_link_extractor(message):
    try:
        pattern = r'https?://\S+'
        link = re.search(pattern, message).group()
        print(link)
        return link
    except AttributeError as e:
        return None
#(wheregoes('http://fkrt.it/_AeT2kNNNN'))

def LinkDirector(link):
    if link.startswith('https://www.ama') or link.startswith('https://www.flipkart'):
        print("getPID returned none")
        return getPID(link)
    elif link.startswith('https://amzn') or link.startswith('http://fkrt') or link.startswith('https://fkrt'):
        return wheregoes(link)
    else:
        print("link red. returned none")
        return None

def getPID(link):
    if link.startswith('https://www.amazon.in/gp/produ'):
        try:
            pid = re.search(f'(?<=product/)\S+(?=/)', link).group()
            return pid
        except Exception as e:
            return None
    elif link.startswith('http://www.flip') or link.startswith('https://www.flip'):
        try:
            fkpid = re.search(r'(?<=p/)[^?]+', link).group()
            fkslug = re.search(r'(?<=com/)[^/]+', link).group()
            print(f"fkpid: --- {fkpid}")
            print(f"fkslud --------- {fkslug}")
            return fkpid, fkslug
        except Exception as e:
            return None;   
    else:
        pid = re.search(r'(?<=p\/)[A-Z0-9]+', link).group()
        return pid
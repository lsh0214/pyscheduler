import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def fetch_page_metadata(url):#반환값은 딕셔너리 형태로 title, favicon_url, 기존 url로 키 구성되어 있어용
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content']
        else:
            title_tag = soup.find('title')
            title = title_tag.string.strip() if title_tag else "제목을 찾을 수 없습니다."

        favicon_url = None
        
        favicon_link = soup.find('link', rel='icon')
        if not favicon_link:
            favicon_link = soup.find('link', rel='shortcut icon')

        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if favicon_link and favicon_link.get('href'):
            favicon_href = favicon_link['href']
            favicon_url = urljoin(base_url, favicon_href)
        else:
            favicon_url = urljoin(base_url, '/favicon.ico')

        return {
            'title': title,
            'favicon_url': favicon_url,
            'url': url
        }

    except requests.exceptions.RequestException as e:
        print(f"요청 오류 ({url}): {e}")
        return {
            'title': "정보를 가져올 수 없습니다.",
            'favicon_url': None,
            'url': url
        }
    except Exception as e:
        print(f"파싱 오류 ({url}): {e}")
        return {
            'title': "정보를 가져올 수 없습니다.",
            'favicon_url': None,
            'url': url
        }
# a=fetch_page_metadata('https://claude.ai/new')
# print("제목: ",a['title'])
# print("바비콘: ",a['favicon_url'])
# print("기존 url",a['url'])
def json_open(file:str)->dict:#입력값( 같은 폴더의 json파일 이름 혹은 절대주소인 str) \ (반환값 딕셔너리 자료형 이름:dict)
    with open(file, "r",encoding='utf-8') as f:
        return json.load(f)
# f=input("원하는 json 파일이름")
# 나는_딕셔너리=json_open(f)
def json_save(file:dict,file_path:str):#매개변수 file은 사용하던 딕셔너리 file_path는 저장할 주소+ 저장할 파일이름
    with open(file_path,'w',encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)
# json_save(나는_딕셔너리,'py2.json')

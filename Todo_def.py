import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime
#동작버전 3.10 이상
#테스트 버전 3.10.19
def url_mention(url):#반환값은 딕셔너리 형태로 title, favicon_url, 기존 url로 키 구성되어 있어용
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
        if "GitHub" in title:
            title="GitHub"
        if "Notion" in title:
            title='Notion'
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
# a=url_mention('https://www.notion.com/ko')
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

def dict_add(new_save:dict,existing:dict|None=None): #매개변수로 새로운 값({날짜:{타이틀들}})형태 입니다 딕셔너리들 배열로 나열 없어요!!, 기존 값(없어도 됨) 리턴 되는 값을 딕셔너리로 활용하면 돼용
    if existing is None:
        new_dict={}
        for key, value in new_save.items():
            new_dict[key] = [value]
        return new_dict
    else:
        for i in new_save.keys():
            if i not in existing.keys():
                existing[i] = [new_save[i]]
            else:
                existing[i].append(new_save[i])
        return existing

# d=dict_add({
#     "2025-10-05": {
#         "title": "Git 개념 학습",
#         "desc": "Git 기초 명령어 학습하기",
#         "link": "https://git-scm.com/book/ko/v2",
#         "completed": False
#     }
# })
# a={
#     "2025-10-05": {
#         "title": "알고리즘 문제 풀이",
#         "desc": "백준 1010번 문제 풀기",
#         "link": "https://www.acmicpc.net/problem/1010",
#         "completed": False
#     }
# }
# print(dict_add(a,d))

def dict_import(new_save:dict,existing:dict|None=None): #이거도 위랑 사용법은 똑같지만 새로운 파일 불러올때 기존 값과 합치거나 기존값 있었나 헷갈릴 수도 있으니까 그냥 넣기
    if existing is None:
        return new_save
    else:
        for i in new_save.keys():
            if i not in existing.keys():
                existing[i] = new_save[i]
            else:
                existing[i].extend(new_save[i])
        return existing
    
def todo_import(existing:dict):#check를 기본값0 엑스 1 세모 2 동그라미 3이라 가정, 입력값에 사용중인 딕셔너리 넣으면 오늘 써야하는 Todo 배열을 넘겨줍니당
    #고려할 점 윤년 + 월별 최대 일자
    day=str(datetime.datetime.now())[0:10]
    day_minus_1=str(datetime.datetime.now()-datetime.timedelta(days=1))[0:10]
    #existing[day] 기본 요소
    try:
        day_minus_1_list=existing[day_minus_1]
    except KeyError:
        return existing.get(day, [])
    if day not in existing:
        existing[day]=[]
    move=[]
    keep=[]
    for i in day_minus_1_list:
        if i['check'] < 3:
            move.append(i)
        else:
            keep.append(i)
    existing[day].extend(move)
    existing[day_minus_1]=keep
    return existing[day]

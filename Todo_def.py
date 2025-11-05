import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime
import copy
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
# a=url_mention('https://claude.ai/')
# print("제목: ",a['title'])
# print("바비콘: ",a['favicon_url'])
# print("기존 url",a['url'])

def json_open(file:str)->dict: #파일이 없거나 손상되었을 때도 프로그램이 다운되지 않고 빈 딕셔너리를 반환합니다.
    try:
        with open(file, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"로그: {file}을(를) 찾을 수 없어 새 딕셔너리를 시작합니다.")
        return {}
    except json.JSONDecodeError:
        print(f"오류: {file} 파일이 손상되었습니다. 새 딕셔너리를 시작합니다.")
        return {}

# f=input("원하는 json 파일이름")
# 나는_딕셔너리=json_open(f)

def json_save(file:dict,file_path:str): # 오류가 발생해도 앱 종료가 멈추지 않도록 print만 합니다.
    """
    [수정됨]
    데이터 저장 시 발생할 수 있는 오류를 처리하기 위해
    try...except 블록을 추가합니다. (앱 종료 안정성)
    """
    try:
        with open(file_path,'w',encoding='utf-8') as f:
            json.dump(file, f, ensure_ascii=False, indent=4)
        print(f"로그: 데이터가 {file_path}에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"오류: 데이터 저장 실패 ({file_path}) - {e}")

# json_save(나는_딕셔너리,'py2.json')

def dict_add(new_save: dict, existing: dict | None = None) -> dict:
    if existing is None:
        existing = {}

    schedule_item = list(new_save.values())[0]

    start_date_str = schedule_item['Start'] 
    start_date = datetime.date.fromisoformat(start_date_str)

    due_date_str = schedule_item.get('Due')
    
    if not due_date_str:
        due_date = start_date
    else:
        due_date = datetime.date.fromisoformat(due_date_str)
        
    current_date = start_date
    while current_date <= due_date:
        date_key = current_date.isoformat()
        item_to_add = copy.deepcopy(schedule_item)
        
        if date_key not in existing:
            existing[date_key] = [item_to_add]
        else:
            existing[date_key].append(item_to_add)
            
        current_date += datetime.timedelta(days=1)
        
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

def dict_import(new_save:dict, start_day:str|None=None, existing:dict|None=None):
    
    data_to_merge = {}

    if start_day:
        try:
            min_key_str = min(new_save.keys())
            min_key_date = datetime.date.fromisoformat(min_key_str)
            
            target_start_date = datetime.date.fromisoformat(start_day)
            
            delta = target_start_date - min_key_date
            
            for old_key_str, value_list in new_save.items():
                old_key_date = datetime.date.fromisoformat(old_key_str)
                new_key_date = old_key_date + delta
                new_key_str = new_key_date.isoformat()
                
                data_to_merge[new_key_str] = value_list
                
        except (ValueError, TypeError) as e:
            print(f"    [경고] 날짜 이동 중 오류 발생: {e}. 원본 new_save를 사용합니다.")
            data_to_merge = new_save
    else:
        data_to_merge = new_save

    if existing is None:
        return data_to_merge
    else:
        for i in data_to_merge.keys():
            if i not in existing:
                existing[i] = data_to_merge[i]
            else:
                existing[i].extend(data_to_merge[i])
        return existing
    
def todo_import(existing:dict):
    day=str(datetime.datetime.now())[0:10]
    day_minus_1=str(datetime.datetime.now()-datetime.timedelta(days=1))[0:10]

    try:
        day_minus_1_list=existing[day_minus_1]
    except KeyError:
        return existing

    existing_dict = existing.get(day, [])
    
    move=[]
    keep=[]
    for i in day_minus_1_list:
        if_1 = i['Status'] < 3
        if_2 = i['NextDay'] == True
        if_3 = (not i['Due']) or (i['Due'] == day_minus_1)
        
        if if_1 and if_2 and if_3:
            move.append(i)
        else:
            keep.append(i)

    existing[day] = move + existing_dict
    existing[day_minus_1]=keep
    
    return existing

def dict_end_edit(existing: dict, item_to_remove: dict) -> dict:
    id_title = item_to_remove['Title']
    id_start = item_to_remove['Start']
    
    start_date_str = item_to_remove['Start']
    due_date_str = item_to_remove.get('Due')

    start_date = datetime.date.fromisoformat(start_date_str)
    
    if not due_date_str:
        due_date = start_date
    else:
        due_date = datetime.date.fromisoformat(due_date_str)

    current_date = start_date
    while current_date <= due_date:
        date_key = current_date.isoformat()
        
        if date_key in existing:
            original_list = existing[date_key]
            
            new_list = [
                item for item in original_list 
                if not (item['Title'] == id_title and item['Start'] == id_start)
            ]
            
            if not new_list:
                del existing[date_key]
            else:
                existing[date_key] = new_list
        
        current_date += datetime.timedelta(days=1)
        
    return existing
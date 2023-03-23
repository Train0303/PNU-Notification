import requests
from bs4 import BeautifulSoup as bs


def get_hakjisi_notice(current_id: int) -> (int, list):
    # id에 대한 버전 관리가 필요함.
    # 얘네는 학지시 로그인 페이지에서 긁어와야 id를 찾을 수 있음.
    url = 'https://onestop.pusan.ac.kr/login'
    response = requests.get(url=url)
    soup = bs(response.text, 'html.parser')

    max_id: int = current_id
    res_items = set()

    for i in range(1, 11): # len(list) == 10
        href: str = soup.select_one(f'#board-tabpanel-1 > ul > li:nth-child({i})').find('a').get('href')

        # href == "javascript:openBbsDetailPop('000000000000386','1303', '126895bc-ae23-5617-29e2-2928567a7bc3')"
        #                                          <고정>        <id>       <[공지]라면 값이 있고, 공지가 아니라면 ''>
        # [공지]글은 이미 올라온 글을 중복해서 올리기 때문에, 중복 제거 처리를 해주어야 하므로, content를 set으로 우선 받는다.

        notice_id = int(href.split(",'")[1].split("'")[0])

        if notice_id > current_id:
            max_id = max(max_id, notice_id)
            notice_title: str = soup.select_one(f'#board-tabpanel-1 > ul > li:nth-child({i}) > a > div.item-title > span.board-title').get_text(strip=True)
            notice_link: str = f'https://onestop.pusan.ac.kr/page?menuCD=000000000000386&mode=DETAIL&seq={notice_id}'
            res_items.add((notice_title, notice_link))

    res_items = sorted(list(res_items), key=lambda x: x[1]) # id가 작은 것부터 오름차순 정렬

    contexts = [{'notice_title': notice_title, 'notice_link': notice_link} for notice_title, notice_link in res_items]

    return max_id, contexts


def get_univ_notice(current_id: int) -> (int, list):
    # id에 대한 버전 관리가 필요함.
    # 얘네는 다른 url에서 긁어와야 함.
    base_url = 'https://www.pusan.ac.kr/kor/CMS/Board/PopupBoard.do'
    univ_url = base_url + '?mgr_seq=3&mode=list'
    response = requests.get(url=univ_url)
    soup = bs(response.text, 'html.parser')

    max_id: int = current_id
    res_items = list()

    for i in range(1, 21): # len(list) == 20
        href: str = soup.select_one(f'#board-wrap > div.board-list-wrap > table > tbody > tr:nth-child({i}) > td.subject > p').find('a').get('href')
        notice_id = int(href.split('=')[-1])

        if notice_id > current_id:
            max_id = max(max_id, notice_id)
            notice_title: str = soup.select_one(f'#board-wrap > div.board-list-wrap > table > tbody > tr:nth-child({i}) > td.subject > p > a').get_text(strip=True)
            notice_link: str = base_url + href
            res_items.append((notice_title, notice_link))

    res_items = sorted(res_items, key=lambda x: x[1]) # id가 작은 것부터 오름차순 정렬

    contexts = [{'notice_title': notice_title, 'notice_link': notice_link} for notice_title, notice_link in res_items]

    return max_id, contexts
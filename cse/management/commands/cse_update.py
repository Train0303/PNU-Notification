# django import
from django.core.management.base import BaseCommand

# command utils import
from cse.management.utils import rss_list

# others import
from typing import *
from requests import get, Response
import xmltodict


class Command(BaseCommand):
    help = '정보컴퓨터공학부 공지사항 확인용입니다.'
    
    
    def handle(self, *args: Any, **options: Any) -> NoReturn:
        response:Response = get(url = 'https://cse.pusan.ac.kr/bbs/cse/2605/rssList.do', 
                                params={ "row" : 20})
        
        if(not response.ok):
            print(response.status_code)
            raise Exception("통신에러")
        
        data:dict = xmltodict.parse(response.text)
        print(data['rss']['channel']['item'])
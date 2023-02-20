# django import
from django import forms
from django.utils import timezone

# model import
from .models import Notice

# others import
from requests import Response, get
import xmltodict


class CreateNoticeForm(forms.Form):
    rss_link = forms.URLField(label='RSS 링크',
                              error_messages={'invalid': '유효한 RSS 링크를 입력해주세요.'})

    def clean(self) -> str:
        rss_link: str = self.cleaned_data.get('rss_link')
        if rss_link:
            rss_link = rss_link.split('?')[0]
            self.cleaned_data['rss_link'] = rss_link
            try:
                rss_response: Response = get(rss_link)
                rss_xml = xmltodict.parse(rss_response.text)
                rss_xml['rss']['channel']['title']

            # 이후 로깅으로 대체 및 예외처리 에러도 구체화(ex: ConnectionError)
            except Exception as e:
                print(e)
                raise forms.ValidationError({
                    'rss_link': 'RSS 링크 인증이 실패했습니다.'
                })

        return self.cleaned_data

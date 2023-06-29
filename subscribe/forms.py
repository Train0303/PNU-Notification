# django import
from django import forms

# models import
from notice.models import Notice
from subscribe.models import Subscribe

# other import
from requests import Response, get
import xmltodict
import re

class CreateSubscribeForm(forms.Form):
    title = forms.CharField(label="등록 제목",
                            error_messages={"invalid": '내용을 입력해주세요.'})
    rss_link = forms.URLField(label="RSS 링크",
                              error_messages={'invalid': '유효한 RSS 링크를 입력해주세요.'})
    notice_link = forms.URLField(label="공지사항 링크",
                                 error_messages={'invalid': '유효한 공지사항 링크를 입력해주세요.'},
                                 required=False)

    def clean_rss_link(self):
        super().clean()
        data: str = self.cleaned_data.get('rss_link')
        if data:
            data = data.split('?')[0]
            self.cleaned_data['rss_link'] = data

            rss_response: Response = get(data)
            if not rss_response.ok:
                raise forms.ValidationError('RSS 링크 인증이 실패했습니다.')

            try:
                rss_xml = xmltodict.parse(rss_response.text)
                rss_xml['rss']['channel']['title']

            # 이후 로깅으로 대체 및 예외처리 에러도 구체화(ex: ConnectionError)
            except Exception as e:
                print(e)
                raise forms.ValidationError('RSS 링크 인증이 실패했습니다.')

        return data

    def clean_notice_link(self):
        notice_link: str = self.cleaned_data.get('notice_link')
        rss_link: str = self.cleaned_data.get('rss_link')

        if notice_link and rss_link:
            notice_response: Response = get(notice_link)
            if not notice_response.ok:
                raise forms.ValidationError('학과 링크 인증이 실패했습니다.')

            rss_link = rss_link.replace('https://', '').split('/')[0]
            notice_link = notice_link.replace('https://', '').split('/')[0]
            if rss_link != notice_link:
                raise forms.ValidationError('RSS와 같은 학과의 링크를 입력해주세요.')

            notice_link = re.sub(r"\?.*", '', self.cleaned_data['notice_link'])
            self.cleaned_data['notice_link'] = notice_link

        return self.cleaned_data.get('notice_link')

    def save(self, save_data):
        Subscribe.objects.create(**save_data)


class UpdateSubscribeForm(forms.Form):
    title = forms.CharField(label="등록 제목",
                            error_messages={"invalid": '내용을 입력해주세요.'})
    rss_link = forms.URLField(label="RSS 링크",
                              error_messages={'invalid': '유효한 RSS 링크를 입력해주세요.'},
                              required=False)

    notice_link = forms.URLField(label="공지사항 링크",
                                 error_messages={'invalid': '유효한 공지사항 링크를 입력해주세요.'},
                                 required=False)

    def clean_notice_link(self):
        notice_link: str = self.cleaned_data.get('notice_link')
        rss_link: str = self.cleaned_data.get('rss_link')

        if notice_link and rss_link:
            notice_response: Response = get(notice_link)
            if not notice_response.ok:
                raise forms.ValidationError('유효한 링크를 입력해주세요.')

            rss_link = rss_link.replace('https://', '').split('/')[0]
            notice_link = notice_link.replace('https://', '').split('/')[0]
            if rss_link != notice_link:
                raise forms.ValidationError('RSS와 같은 학과의 링크를 입력해주세요.')

            notice_link = re.sub(r"\?.*", '', self.cleaned_data['notice_link'])
            self.cleaned_data['notice_link'] = notice_link

        return self.cleaned_data.get('notice_link')


class UpdateHakjisiSubscribeForm(forms.Form):
    title = forms.CharField(label="등록 제목",
                            error_messages={"invalid": '내용을 입력해주세요.'})
from typing import *

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DeleteView

from notice.models import HakjisiNotice
from subscribe.models import Subscribe, HakjisiSubscribe
from .async_send_mail import async_send_mail
from .forms import EmailAuthenticationForm, CustomUserCreationForm
from .permission import UserPermissionRequiredMixin
from .token import EmailVerificationTokenGenerator

User = get_user_model()

class SignUpView(auth_views.FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('registration:verification') # 이메일 인증 template으로 이동

    def get(self, request, *args, **kwargs): # 1차 경고 메시지
        if User.objects.filter(is_active=True).count() > 500:
            messages.warning(request, "죄송합니다. 현재 사용자가 가득 차서 회원가입이 불가능합니다.")

        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        if User.objects.filter(is_active=True).count() > 500: # 실제 회원가입 차단
            messages.warning(self.request, "죄송합니다. 현재 사용자가 가득 차서 회원가입이 불가능합니다.")
            return super().form_invalid(form)

        user = form.save(commit=False)
        user.email = form.cleaned_data.get('email')
        user.save()
        login(self.request, user)
        send_verification_email(self.request)
        return super().form_valid(form)


class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True # 이미 로그인 된 사용자라면, `LOGIN_REDIRECT_URL`로 이동, `settings.py`에 '/'로 정의.


class EmailVerificationResultView(View):
    def get(self, request, uidb64, token):

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if user.is_active: # 이미 이메일 인증에 성공한 상태에서 다시 한번 링크를 누를 경우,
                return render(request, 'registration/verification_result.html')  # 성공 page로 이동
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user != request.user:
            return render(request, 'registration/verification_result.html', context={'user': user})

        if user is not None and EmailVerificationTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()

            hakjisi_notice = HakjisiNotice.objects.get(title="학지시공지")
            univ_notice = HakjisiNotice.objects.get(title="대학공지")

            # user가 active되는 순간에, 학생지원시스템의 공지사항을 default로 제공한다.
            subscribe_hakjisi = HakjisiSubscribe(title='학지시공지', user=user, notice=hakjisi_notice, is_active=False)
            subscribe_hakjisi.save()

            subscribe_univ = HakjisiSubscribe(title='대학공지', user=user, notice=univ_notice, is_active=False)
            subscribe_univ.save()

        return render(request, 'registration/verification_result.html', context={'user':user})


# Password관련 View는 auth_views의 Class를 Override하여, 경로만 바꿔주었습니다.
class PasswordResetView(auth_views.PasswordResetView):
    """
    비밀번호 초기화 - 사용자 email 입력
    + 찾고자 하는 이메일이 없다면, 메일 발송 하지 않음
    """
    success_url = reverse_lazy('registration:password_reset_done')
    html_email_template_name = 'registration/password_reset_email.html'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            return super().post(request, *args, **kwargs)
        except User.DoesNotExist:
            context = {'msg': f"{email} : 존재하지 않는 이메일입니다. 회원가입을 진행해주세요."}
            return render(request, 'registration/password_reset_form.html', context=context)


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """
    비밀번호 초기화 - 메일 전송 완료
    """
    template_name = 'registration/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    비밀번호 초기화 - 새로운 비밀번호 입력
    """
    success_url = reverse_lazy('registration:password_reset_complete')


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    비밀번호 초기화 - 비밀번호 변경 완료
    """
    template_name = 'registration/password_reset_complete.html'


class AuthDeleteView(UserPermissionRequiredMixin, DeleteView):
    model = User
    pk_url_kwarg = 'pk'
    template_name = 'registration/withdrawal.html'
    success_url = reverse_lazy('registration:index')
    check_permission_path_variable = 'pk'


def send_verification_email(request):
    """
    현재 로그인 중인 유저에게 인증 메일을 보내는 함수
    """
    user = request.user
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk)).encode().decode()
    token = EmailVerificationTokenGenerator().make_token(user)
    verification_url = reverse('registration:verification_result', args=[uid, token])
    verification_link = 'http://' + current_site.domain + verification_url

    async_send_mail(
        subject='[PNU-Notification] Verify Your Email',
        html_template = 'registration/verification_email.html',
        context={
            'verification_link': verification_link,
        },
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def index(request):
    """
    프로젝트 메인 페이지
    비로그인: 로그인 페이지 렌더
    미인증: 인증 요청 페이지 렌더
    로그인: 구독한 목록을 보여준다.
    """
    user = request.user
    if not user.is_authenticated:
        return render(request, 'start.html')

    if not user.is_active:
        return render(request, 'registration/verification_need.html')

    subscribes: List[Subscribe] = Subscribe.objects.select_related('notice').filter(user=user)
    hakjisi_subscribes: List[HakjisiSubscribe] = HakjisiSubscribe.objects.select_related('notice').filter(user=user)
    context_data = {
        'subscribes': list(
            map(lambda subscribe: {
                'id': subscribe.id,
                'title': subscribe.title,
                'RSS': subscribe.notice.rss_link,
                'last_updated': subscribe.notice.updated_at,
                'is_active': subscribe.is_active
            }, subscribes)
        ),
        'hakjisi_subscribes': list(
            map(lambda hakjisi_subscribe: {
                'id': hakjisi_subscribe.id,
                'title': hakjisi_subscribe.title,
                'notice_link': hakjisi_subscribe.notice.notice_link,
                'is_active': hakjisi_subscribe.is_active
            }, hakjisi_subscribes)
        )
    }

    return render(request, 'registration/index.html', context=context_data)


@login_required
def verification(request):
    if not request.user.is_active:
        return render(request, 'registration/verification.html')
    return redirect('registration:index')


@login_required
def verification_retry(request):
    if request.method == 'POST':
        send_verification_email(request)
        return redirect('registration:verification')
    return redirect('registration:index')


def check_email_duplication(request):
    email = request.GET.get('email', None)
    data = {
        'is_exists': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)
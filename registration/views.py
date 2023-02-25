from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from .forms import EmailAuthenticationForm, CustomUserCreationForm
from .token import EmailVerificationTokenGenerator


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('registration:verification') # 이메일 인증 template으로 이동

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data.get('email')
        user.save()
        login(self.request, user)
        return super().form_valid(form)


class EmailLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True # 이미 로그인 된 사용자라면, `LOGIN_REDIRECT_URL`로 이동, `settings.py`에 '/'로 정의.


class EmailVerificationEnableView(View):
    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if user.is_active: # 이미 이메일 인증에 성공한 상태에서 다시 한번 링크를 누를 경우,
                return render(request, 'registration/verification_result.html')  # 성공 page로 이동
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and EmailVerificationTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
        return render(request, 'registration/verification_result.html')


@login_required
def send_verification_email(request):
    user = request.user
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk)).encode().decode()
    token = EmailVerificationTokenGenerator().make_token(user)
    verification_url = reverse('registration:verification_enable', args=[uid, token])
    verification_link = 'http://' + current_site.domain + verification_url

    print(f'verification_link : {verification_link}')
    send_mail(
        'verify your email',
        f'아래 링크를 눌러 이메일 인증을 완료해주세요:\n\n{verification_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def index(request):
    return render(request, 'index.html')


@login_required
def verification(request):
    send_verification_email(request)
    return render(request, 'registration/verification.html')


def check_email_duplication(request):
    email = request.GET.get('email', None)
    User = get_user_model()
    data = {
        'is_exists': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)
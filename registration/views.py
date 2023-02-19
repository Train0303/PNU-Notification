from django.contrib.auth import login
from django.contrib.auth.views import LoginView, FormView
from django.urls import reverse_lazy

from .forms import EmailAuthenticationForm, CustomUserCreationForm


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('registration:index') # 회원가입에 성공하면, 'index'로 이동

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


### index test ###
from django.shortcuts import render
def index(request):
    return render(request, 'base.html')
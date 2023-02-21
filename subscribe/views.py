from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import CreateSubscribeForm
from .models import Subscribe
from notice.models import Notice


# Create your views here.
class CreateSubscribeView(LoginRequiredMixin, FormView):
    template_name: str = 'subscribe/create_subscribe.html'
    form_class = CreateSubscribeForm
    success_url = reverse_lazy('registration:index')
    login_url = reverse_lazy('registration:login')

    def form_valid(self, form):
        notice, created = Notice.objects.get_or_create(rss_link=form.cleaned_data.get("rss_link"))
        if Subscribe.objects.filter(notice=notice, user=self.request.user).exists():
            messages.warning(self.request, "중복된 RSS링크가 존재합니다.")
            return redirect("subscribe:create-subscribe")

        save_data = {
            'user': self.request.user,
            'notice': notice,
            'notice_link': form.cleaned_data.get("notice_link")
        }

        form.save(save_data)
        return redirect(self.success_url)

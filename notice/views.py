from django.db import DatabaseError,transaction
from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import CreateNoticeForm
from .models import Notice


# Create your views here.
class CreateNoticeView(FormView):
    template_name: str = 'notice/create_notice.html'
    form_class = CreateNoticeForm
    success_url: str = reverse_lazy('registration:index')

    @transaction.atomic()
    def form_valid(self, form):
        rss_link = form.cleaned_data.get('rss_link')
        try:
            Notice.objects.create(rss_link=rss_link)
        except DatabaseError as e:
            messages.warning(self.request, "중복된 RSS링크가 존재합니다.")
            return redirect('notice:notice-create')

        return super().form_valid(form)


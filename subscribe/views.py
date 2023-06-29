import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, View

from notice.models import Notice
from subscribe.models import HakjisiSubscribe
from .forms import CreateSubscribeForm, UpdateSubscribeForm, UpdateHakjisiSubscribeForm
from .models import Subscribe
from .permission import WriterPermissionRequiredMixin, HakjisiWriterPermissionRequiredMixin


# Create your views here.
class CreateSubscribeView(LoginRequiredMixin, FormView):
    template_name: str = 'subscribe/create_subscribe.html'
    form_class = CreateSubscribeForm
    success_url = reverse_lazy('registration:index')
    login_url = reverse_lazy('registration:login')

    @transaction.atomic()
    def form_valid(self, form):
        if Subscribe.objects.filter(user_id=self.request.user.id).count() == 10:
            messages.warning(self.request, "RSS 구독은 최대 10개까지 가능합니다.")
            return render(self.request, self.template_name, {'form': form})

        notice, created = Notice.objects.get_or_create(rss_link=form.cleaned_data.get("rss_link"))

        if Subscribe.objects.filter(notice=notice, user=self.request.user).exists():
            messages.warning(self.request, "중복된 RSS링크가 존재합니다.")
            return render(self.request, self.template_name, {'form': form})

        save_data = {
            'user': self.request.user,
            'notice': notice,
            'notice_link': form.cleaned_data.get('notice_link'),
            'title': form.cleaned_data.get('title')
        }

        form.save(save_data)
        return redirect(self.success_url)


class UpdateSubscribeView(WriterPermissionRequiredMixin, View):
    template_name: str = 'subscribe/update_subscribe.html'
    success_url: str = reverse_lazy('registration:index')
    login_url: str = reverse_lazy('registration:login')
    queryset = Subscribe.objects.select_related("notice")
    check_permission_path_variable = 'pk'

    def get_object(self, pk):
        return get_object_or_404(Subscribe.objects.select_related("notice"), pk=pk)

    def get(self, request, pk):
        subscribe = self.get_object(pk)

        return render(request, self.template_name, {
            "subscribe": subscribe
        })

    def post(self, request, pk):
        context = self.request.POST
        form = UpdateSubscribeForm(context)
        if not form.is_valid():
            messages.warning(self.request, form.errors)
            return redirect(reverse("subscribe:update-subscribe", args=(pk,)))

        subscribe: Subscribe = self.get_object(pk)
        subscribe.title = form.cleaned_data.get('title')
        subscribe.notice_link = form.cleaned_data.get('notice_link')
        subscribe.save()

        return redirect(self.success_url)


class UpdateHakjisiSubscribeView(HakjisiWriterPermissionRequiredMixin, View):
    template_name: str = 'subscribe/update_hakjisi_subscribe.html'
    success_url: str = reverse_lazy('registration:index')
    login_url: str = reverse_lazy('registration:login')
    queryset = HakjisiSubscribe.objects.select_related("notice")
    check_permission_path_variable = 'pk'

    def get_object(self, pk):
        return get_object_or_404(HakjisiSubscribe.objects.select_related("notice"), pk=pk)

    def get(self, request, pk):
        hakjisi_subscribe = self.get_object(pk)

        return render(request, self.template_name, {
            "hakjisi_subscribe": hakjisi_subscribe,
            'notice_link': hakjisi_subscribe.notice.notice_link,
        })

    def post(self, request, pk):
        context = self.request.POST
        form = UpdateHakjisiSubscribeForm(context)
        if not form.is_valid():
            messages.warning(self.request, form.errors)
            return redirect(reverse("subscribe:update-hakjisi-subscribe", args=(pk,)))

        hakjisi_subscribe: HakjisiSubscribe = self.get_object(pk)
        hakjisi_subscribe.title = context.get('title')
        hakjisi_subscribe.save()

        return redirect(self.success_url)


class UpdateSubscribeActiveView(WriterPermissionRequiredMixin, View):
    login_url: str = reverse_lazy('registration:login')
    queryset = Subscribe.objects.select_related("notice")
    check_permission_path_variable = 'pk'

    def get_object(self, pk):
        return get_object_or_404(Subscribe, pk=pk)

    def post(self, request, pk):
        data = json.loads(self.request.body)
        state = data.get('state')
        if state is None:
            return JsonResponse(status=400, data={
                'status': 'false',
                'message': '올바른 호출이 아닙니다.(state)'
            })

        subscribe = self.get_object(pk)
        subscribe.is_active = state
        subscribe.save()

        return JsonResponse(status=200, data={
            'status': 'success',
            'message': {
                'is_active': subscribe.is_active
            }
        })


class DeleteSubscribeView(WriterPermissionRequiredMixin, View):
    model = Subscribe
    success_url: str = reverse_lazy('registration:index')
    check_permission_path_variable = 'pk'

    def get_object(self, pk):
        return get_object_or_404(Subscribe, pk=pk)

    def post(self, request, pk):
        subscribe: Subscribe = self.get_object(pk)
        subscribe.delete()
        return redirect(self.success_url)


class UpdateHakjisiSubscribeActiveView(HakjisiWriterPermissionRequiredMixin, View):
    login_url: str = reverse_lazy('registration:login')
    queryset = HakjisiSubscribe.objects.select_related("hakjisinotice")
    check_permission_path_variable = 'pk'

    def get_object(self, pk):
        return get_object_or_404(HakjisiSubscribe, pk=pk)

    def post(self, request, pk):
        data = json.loads(self.request.body)
        state = data.get('state')
        if state is None:
            return JsonResponse(status=400, data={
                'status': 'false',
                'message': '올바른 호출이 아닙니다.(state)'
            })

        subscribe = self.get_object(pk)
        subscribe.is_active = state
        subscribe.save()

        return JsonResponse(status=200, data={
            'status': 'success',
            'message': {
                'is_active': subscribe.is_active
            }
        })

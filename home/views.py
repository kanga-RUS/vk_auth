import os

from django.shortcuts import render
from django.views.generic import TemplateView

import requests
from requests.exceptions import ConnectionError, RequestException

API_VERSION = '5.103'


class HomePageView(TemplateView):
    template_name = 'home/home.html'

    def dispatch(self, request, *args, **kwargs):
        return super(HomePageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            self.request.session['user_vk_id'] = \
                self.request.user.socialaccount_set.all()[0].extra_data['id']
        return context


def search(request):
    result = dict()
    user_id = request.session['user_vk_id']

    if request.method == 'GET':
        search_text = request.GET['q']
        if search_text:
            try:
                req_str = "https://api.vk.com/method/friends.search?user_id={uid}&fields=first_name,last_name,domain&count=1000&q={q}&access_token={token}&v={api_version}".format(
                    uid=user_id,
                    q=search_text,
                    token=os.environ.get('VK_TOKEN'),
                    api_version=API_VERSION
                )
                result = requests.get(req_str).json().get('response')
            except (ConnectionError, RequestException) as e:
                context = {'error': e}
                return render(request, 'home/search_result.html',
                              context=context)
    context = {'result': result}

    return render(request, 'home/search_result.html', context=context)

import re

from django.shortcuts import render
from django.views.generic import TemplateView

from vk_auth.settings import vk

USERID_PATTERN = r'(\d+)'


class HomePageView(TemplateView):
    template_name = 'home/home.html'


def search(request):
    result = dict()
    user_id = int(re.search(USERID_PATTERN, request.user.username).group(1))
    if request.method == 'GET':
        search_text = request.GET['q']
        if search_text:
            result = vk.friends.search(user_id=user_id,
                                        fields='first_name,last_name,domain',
                                        count=1000,
                                        q=search_text)
    context = {'result': result}

    return render(request, 'home/search_result.html', context=context)

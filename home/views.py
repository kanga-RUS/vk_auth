from django.shortcuts import render
from django.views.generic import TemplateView

from allauth.socialaccount.models import SocialToken
import requests
from requests.exceptions import ConnectionError, RequestException

API_VERSION = '5.103'


class HomePageView(TemplateView):
    template_name = 'home/home.html'

    def dispatch(self, request, *args, **kwargs):
        return super(HomePageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous and self.request.user.socialaccount_set.all():
            self.request.session['user_vk_id'] = \
                self.request.user.socialaccount_set.all()[0].extra_data['id']
            access_token = SocialToken.objects.get(account__user=self.request.user,
                                                   account__provider='vk')
            self.request.session['access_token'] = access_token.token
        return context


def search(request):
    context = dict()

    if request.method == 'GET':
        search_text = request.GET['q']
        if search_text:
            try:
                req_str = "https://api.vk.com/method/friends.search?user_id={uid}&fields=first_name,last_name,domain&count=1000&q={q}&access_token={token}&v={api_version}".format(
                    uid=request.session['user_vk_id'],
                    q=search_text,
                    token=request.session['access_token'],
                    api_version=API_VERSION
                )
                resp = requests.get(req_str)
            except (ConnectionError, RequestException) as e:
                context = {'error': e}
                return render(request, 'home/search_result.html',
                              context=context)
            res = resp.json()
            if resp.status_code == 200 and not res.get('error'):
                context = {'result': res.get('response')}
            else:
                context = {'error': res.get('error').get('error_msg')}
    return render(request, 'home/search_result.html', context=context)

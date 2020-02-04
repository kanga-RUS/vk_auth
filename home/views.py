from django.shortcuts import render
from django.views.generic import TemplateView

from vk_auth.settings import vk


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
            result = vk.friends.search(user_id=user_id,
                                       fields='first_name,last_name,domain',
                                       count=1000,
                                       q=search_text)
    context = {'result': result}

    return render(request, 'home/search_result.html', context=context)

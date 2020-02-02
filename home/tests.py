import os

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialLogin
from allauth.utils import get_user_model


class TestGeneral(TestCase):
    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home/home.html')

    def test_home_page_view_not_login(self):
        resp = self.client.get('/')
        self.assertContains(resp, '/accounts/vk/login/')


class TestStaff(TestCase):
    def setUp(self):
        self.test_admin_password = 'mypassword'
        self.test_admin_user = User.objects.create_superuser('myuser',
                                                             'myemail@test.com',
                                                             self.test_admin_password)

    def test_non_social_account_login(self):
        r = self.client.login(username=self.test_admin_user.username,
                              password=self.test_admin_password)
        self.assertTrue(r)
        resp = self.client.get('/')
        self.assertContains(resp, 'Your account have')

    def test_non_social_account_logout(self):
        self.test_non_social_account_login()
        resp = self.client.get('/accounts/logout/', follow=True)
        self.assertRedirects(resp, '/', status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)


class TestSocialAuth(TestCase):
    def setUp(self):
        site = Site.objects.get_current()
        for provider in providers.registry.get_list():
            app = SocialApp.objects.create(
                provider=provider.id,
                name=provider.id,
                client_id=os.environ.get('VK_CLIENT_ID'),
                key=os.environ.get('VK_KEY'),
                secret=os.environ.get('VK_APP_SECRET'))
            app.sites.add(site)

    def test_social_account_taken_at_signup(self):
        session = self.client.session
        TUser = get_user_model()
        sociallogin = SocialLogin(
            user=TUser(email=os.environ.get('VK_LOGIN')),
            account=SocialAccount(
                provider='vk'
            ),
        )
        session['socialaccount_sociallogin'] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse('socialaccount_signup'))
        form = resp.context['form']
        self.assertEqual(form['email'].value(), os.environ.get('VK_LOGIN'))
        resp = self.client.post(
            reverse('socialaccount_signup'),
            data={'username': os.environ.get('VK_UID'),
                  'email': os.environ.get('VK_LOGIN')}, follow=True)
        self.assertRedirects(resp, '/', status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(SocialAccount.objects.count(), 1)

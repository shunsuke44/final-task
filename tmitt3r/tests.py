from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Tm33t, Reply, Retm33t
import time

no_csrf_middleware = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD = 'SamplePassword'

def create_user_by_id(obj, id):
    username = obj.__class__.__name__ + str(id)
    user = User.objects.create_user(username=username, password=PASSWORD)
    return user

def create_text(obj, id):
    return 'This is ' + obj.__class__.__name__ + str(id) + ' Sample Text.'


class HomeViewTests(TestCase):
    def setUp(self):
        username = 'HomeViewTestClient'
        password = 'SamplePassword'
        self.user = User.objects.create_user(username=username, 
                                             password=password)
        self.client.login(username=username, password=password)
        self.text_list = []
        for i in range(20):
            text = 'This is HomeViewTest Tm33t text No.{}.'.format(i)
            Tm33t.objects.create(poster=self.user, content=text)
            self.text_list.append(text)
            time.sleep(0.1)
        self.text_list.reverse()
    
    def test_home_view_context(self):
        """
        HomeViewによって、contextとしてログインユーザーの
        直近の10個のTm33tがlatest_tm33t_listとして
        受け渡される。
        """
        res = self.client.get(reverse('tmitt3r:home'))
        queryset = res.context['latest_tm33t_list']
        for i in range(10):
            self.assertEqual(queryset[i].content, self.text_list[i])    


@override_settings(MIDDLEWARE=no_csrf_middleware)
class Tm33tViewTests(TestCase):
    def setUp(self):
        self.username = 'Tm33tViewTest'
        self.password = 'SamplePassword'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
    
    def test_tm33t(self):
        """
        ツイートが成功するとデータベースに登録され、
        posterは投稿者に、post_timeは投稿時の時間になる。
        """
        url = reverse('tmitt3r:tm33t')
        text = 'This is sample tm33t for Tm33tViewTest.'
        data = {'content': text}
        time = timezone.now()
        self.client.post(url, data=data)
        tm33t = Tm33t.objects.filter(
                            poster__username=self.username
                        ).get(
                            post_time__gte=time
                        )
        self.assertEqual(tm33t.content, text)


class Tm33tModelTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='Tm33tModelTests1')
        self.u2 = User.objects.create_user(username='Tm33tModelTests2')
        self.u3 = User.objects.create_user(username='Tm33tModelTest3')
        self.t1 = Tm33t.objects.create(poster=self.u1, content=create_text(self, 1))

    def test_has_been_liked(self):
        """
        has_been_liked メソッドのテスト
        引数にはUserオブジェクトかusernameを取り、
        users_likedに含まれていればTrueを返す。
        """
        self.t1.users_liked.add(self.u2)
        self.assertTrue(self.t1.has_been_liked(self.u2))
        self.assertFalse(self.t1.has_been_liked(self.u3))
        self.assertTrue(self.t1.has_been_liked(self.u2.get_username()))
        self.assertFalse(self.t1.has_been_liked(self.u3.get_username()))
        self.t1.users_liked.remove(self.u2)
        self.assertFalse(self.t1.has_been_liked(self.u2))
    
    def test_is_reply(self):
        """
        Tm33tオブジェクトがReplyに継承されたものである場合に
        is_reply() はTrueを返す
        """
        text = create_text(self, 2)
        # Replyオブジェクトとして作成
        reply = Reply.objects.create(poster=self.u1, related_tm33t=self.t1, content=text)
        # tm33tオブジェクトとして取得
        tm33t = Tm33t.objects.get(content=text)
        self.assertTrue(reply.is_reply())
        self.assertTrue(tm33t.is_reply())
    
    def test_is_not_reply(self):
        """
        Tm33tオブジェクトがReplyでない場合には
        is_reply()はFalseを返す
        """
        self.assertFalse(self.t1.is_reply())
    
    def test_is_retm33t(self):
        """
        Tm33tオブジェクトがRetm33tに継承されたものである場合に
        is_retm33t() はTrueを返す
        """
        text = create_text(self, 3)
        # Replyオブジェクトとして作成
        retm33t = Retm33t.objects.create(poster=self.u1, tm33t_retm33ted=self.t1, content=text)
        # tm33tオブジェクトとして取得
        tm33t = Tm33t.objects.get(content=text)
        self.assertTrue(retm33t.is_retm33t())
        self.assertTrue(tm33t.is_retm33t())
    
    def test_is_not_retm33t(self):
        """
        Tm33tオブジェクトがRetm33tでない場合には
        is_retm33t()はFalseを返す
        """
        self.assertFalse(self.t1.is_retm33t())


@override_settings(MIDDLEWARE=no_csrf_middleware)
class Tm33tLikeFeatureTests(TestCase):
    def setUp(self):
        # create users
        self.user = create_user_by_id(self, 'User')
        self.poster = create_user_by_id(self, 'Poster')
        # create target tm33t
        self.text1 = create_text(self, 1)
        self.text2 = create_text(self, 2)
        self.tm33t1 = Tm33t.objects.create(poster=self.poster, content=self.text1)
        self.tm33t2 = Tm33t.objects.create(poster=self.poster, content=self.text2)
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # post target url
        self.url = reverse('tmitt3r:like')

    def test_like_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドで適切なデータを与えると
        そのユーザーが対象のツイートにライクする。
        """
        res = self.client.post(self.url, data={'like': 'like', 'pk': self.tm33t1.pk})
        self.assertEqual(200, res.status_code)
        self.assertTrue(self.tm33t1.users_liked.filter(username=self.user.username).exists())

    def test_unlike_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドで適切なデータを与えると
        そのユーザーが対象のツイートのライクを外す。
        """
        self.tm33t2.users_liked.add(self.user)
        self.assertTrue(self.tm33t2.users_liked.filter(username=self.user.username).exists())
        # tm33t2に対するUnlike
        res = self.client.post(self.url, data={'like': 'unlike', 'pk': self.tm33t2.pk})
        self.assertEqual(200, res.status_code)
        self.assertFalse(self.tm33t2.users_liked.filter(username=self.user.username).exists())


class Tm33tReplyViewTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:reply', kwargs={'pk': self.tm33t.pk})
    
    def test_reply_post(self):
        """
        ReplyをPOSTするとホーム画面にリダイレクトされ、データベースに登録される。
        """
        text = create_text(self, 2)
        redirect_url = reverse('tmitt3r:home')
        res = self.client.post(self.url, data={'content': text})
        self.assertRedirects(res, redirect_url)
        self.assertTrue(Reply.objects.filter(content=text).exists())


class Retm33tViewTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:retm33t')
    
    def test_retm33t_post(self):
        """
        Retm33tビューにtm33tのpkをPOSTすると、そのtm33tをRetm33tする。
        """
        res = self.client.post(self.url, data={'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertTrue(Retm33t.objects.filter(tm33t_retm33ted=self.tm33t).exists())


class Unretm33tTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:unretm33t')
    
    def test_unretm33t_post(self):
        """
        Unretm33tビューにTm33tのpkをPOSTすると、そのTm33tのRetm33tを削除する。
        """
        Retm33t.objects.create(poster=self.user, tm33t_retm33ted=self.tm33t)
        res = self.client.post(self.url, data={'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertFalse(Retm33t.objects.filter(poster=self.user, tm33t_retm33ted=self.tm33t).exists())

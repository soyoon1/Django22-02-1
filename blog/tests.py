from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post   # 우리 포스트.py에서 모델들을 들고 오겠다.

# Create your tests here.
class  TestView(TestCase):

    def setUp(self):
        self.client = Client()

    def nav_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)

    def test_post_list(self):  # 함수는 소문자로 시작
        # self.assertEqual(3,3)   괄호안에 있는 두 개의 값은 값다. 같으면 True 다르면 False setUp 함수는 초기화 함수
        response = self.client.get('/blog/')
        # reponse 결과가 정상적인지
        self.assertEqual(response.status_code, 200) # 200이면 페이지 보여준 것 아니면 페이지 못 보여준 것.

        soup = BeautifulSoup(response.content, 'html.parser')
        # title이 정상적으로 보이는지
        self.assertEqual(soup.title.text, 'Blog')

        # navbar가 정상적으로 보이는지
        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        # post가 정상적으로 보이는지 등을 테스트해야 한다.
        # 1. 맨 처음엔 Post가 하나도 안 보임
        self.assertEqual(Post.objects.count(),0)
        main_area = soup.find('div', id="main-area")
        self.assertIn('아무 게시물이 없습니다.', main_area.text)

        # 2. Post가 있는 경우
        post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다")
        post_002 = Post.objects.create(title="두번째 포스트", content="두번째 포스트입니다")
        self.assertEqual(Post.objects.count(), 2)

        response = self.client.get('/blog/')  # html문서 가져올 때마다 테스트 해 줘야 함.
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id="main-area")
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('아무 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다")
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # navbar = soup.nav
        # self.assertIn('Blog', navbar.text)
        # self.assertIn('AboutMe', navbar.text)
        self.nav_test(soup)

        self.assertIn(post_001.title, soup.title.text)

        main_area=soup.find('div', id='main-area')
        #post_area=soup.find('div', id='post-area')  한 번 찾고 또 처음으로 가서 다시 찾음
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        self.assertIn(post_001.content, post_area.text)
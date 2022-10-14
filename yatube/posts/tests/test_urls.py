from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200,
                         'Код главной страницы != 200'
                         )

    def test_about_url_exists_at_desired_location_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200,
                         'Код страницы about!= 200'
                         )

    def test_about_url_uses_correct_template_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_url_exists_at_desired_location_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200,
                         'Код страницы tech != 200'
                         )

    def test_about_url_uses_correct_template_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.authorized = User.objects.create_user(username='authorized')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized)

    def test_urls_uses_correct_template(self):
        """"Проверка шаблонов для неавторизованных пользователей"""
        templates_urls_name = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/test_unexisting': 'core/404.html',
        }
        for address, template in templates_urls_name.items():
            cache.clear()
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """"Проверка работы URL-ссылок status_code = 200"""
        templates_urls_name = ['/', '/group/test-slug/',
                               '/profile/auth/', f'/posts/{self.post.pk}/',
                               ]
        for address in templates_urls_name:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200,
                                 'status_code != 200'
                                 )

    def test_create_uses_correct_template(self):
        response = self.author_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html',
                                'Шаблон posts/create_post.html не вызван'
                                )

    def test_create_exist_at_desired_location(self):
        response = self.author_client.get('/create/')
        self.assertEqual(response.status_code, 200,
                         'status_code != 200'
                         )

    def test_edit_uses_correct_template(self):
        response = self.author_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html',
                                'Шаблон posts/create_post.html не вызван'
                                )

    def test_edit_exist_at_desired_location(self):
        response = self.author_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200,
                         'status_code != 200'
                         )

    def test_unexisting_page(self):
        response = self.guest_client.get('/test_unexisting/')
        self.assertEqual(response.status_code, 404,
                         'Код несуществующей страницы != 404'
                         )

    def test_guest_cannot_get_and_post_create_request(self):
        response_get = self.guest_client.get('/create/')
        response_post = self.guest_client.post(
            '/create/',
            text='POST from guest',
        )
        self.assertEqual(response_get.status_code, 302)
        self.assertEqual(response_post.status_code, 302)

    def test_no_author_cannot_get_and_post_edit_request(self):
        response_get = self.authorized_client.get(
            f'posts/{self.post.pk}post_edit'
        )
        response_post = self.authorized_client.post(
            f'posts/{self.post.pk}post_edit',
            text='POST from no_author',
        )
        self.assertEqual(response_get.status_code, 404)
        self.assertEqual(response_post.status_code, 404)

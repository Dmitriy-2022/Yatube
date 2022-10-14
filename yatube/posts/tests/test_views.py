from django import forms
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache


from ..models import Post, Group, Comment, Follow


User = get_user_model()


class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_client = Client()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(username='authorized')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_without_post = Group.objects.create(
            title='Пустая группа',
            slug='empty-slug',
            description='Тут должно быть пусто',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.author,
            post_id=cls.post.pk,
        )

    def setUp(self):
        cache.clear()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_templates(self):
        template_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}
                    ): 'posts/create_post.html',
        }

        for reverse_name, template in template_pages_name.items():
            cache.clear()
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        atr_of_obj = {
            response.context['page_obj'][0].text: self.post.text,
            response.context['page_obj'][0].image: self.post.image,
        }
        for respose_field, obj_field in atr_of_obj.items():
            with self.subTest(respose_field=respose_field):
                self.assertEqual(respose_field, obj_field)

    def test_group_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        response = self.guest_client.get(reverse('posts:index'))
        atr_of_obj = {
            response.context['page_obj'][0].text: self.post.text,
            response.context['page_obj'][0].image: self.post.image,
            response.context['page_obj'][0].group.title: self.group.title,
        }
        for respose_field, obj_field in atr_of_obj.items():
            with self.subTest(respose_field=respose_field):
                self.assertEqual(respose_field, obj_field)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}
                    )
        )
        atr_of_obj = {
            response.context['page_obj'][0].text: self.post.text,
            response.context['page_obj'][0].image: self.post.image,
            response.context['page_obj'][0].author: self.post.author,
        }
        for respose_field, obj_field in atr_of_obj.items():
            with self.subTest(respose_field=respose_field):
                self.assertEqual(respose_field, obj_field)

    def test_post_detail_page_show_correct_context(self):
        data_add = {
            'text': 'Комментарий в post_detail',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=data_add,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )

        atr_of_obj = {
            response.context['post'].text: self.post.text,
            response.context['post'].image: self.post.image,
            response.context['comments'][0].text: data_add.get('text'),
            response.context['post'].author.posts.count():
                self.post.author.posts.count(),
        }
        for respose_field, obj_field in atr_of_obj.items():
            with self.subTest(respose_field=respose_field):
                self.assertEqual(respose_field, obj_field)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_post_with_group_displayed(self):
        dict_post_group = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}
                    ),
        ]

        for reverse_name in dict_post_group:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_with_group_in_correct_group(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group_without_post.slug}'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_guest_cannot_get_and_post_create_request(self):
        response_get = self.guest_client.get('posts:post_create')
        response_post = self.guest_client.post(
            reverse('posts:post_create'),
            text='POST from guest',
        )
        self.assertEqual(response_get.status_code, 404)
        self.assertEqual(response_post.status_code, 302)

    def test_no_author_cannot_get_and_post_edit_request(self):
        test_kwargs = {'post_id': self.post.pk}

        response_get = self.authorized_client.get('posts:post_edit',
                                                  kwargs=test_kwargs)
        response_post = self.authorized_client.post(
            reverse('posts:post_edit', kwargs=test_kwargs),
            text='POST from no_author',
        )
        self.assertEqual(response_get.status_code, 404)
        self.assertEqual(response_post.status_code, 302)

    def test_no_authorized_cannot_commenting(self):
        data_com = {
            'text': '2-Тестовый комментарий'
        }
        reverse_add = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk})
        count_comment = Comment.objects.count()

        self.guest_client.post(
            reverse_add,
            data=data_com,
        )
        self.assertEqual(Comment.objects.count(), count_comment)

        self.authorized_client.post(
            reverse_add,
            data=data_com,
        )
        self.assertEqual(Comment.objects.count(), count_comment + 1)


class PostCacheTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_posts_cache(self):
        self.guest_client.get(reverse("posts:index"))
        text = "Проверка кеширования"
        Post.objects.create(text=text, author=self.author)
        response = self.guest_client.get(reverse("posts:index"))
        self.assertNotContains(response, text)


class FollowTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized = User.objects.create(username='auth')
        cls.authorized_client = Client()
        cls.author = User.objects.create(username='author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client.force_login(self.authorized)

    def test_auth_can_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author}))
        self.assertTrue(
            Follow.objects.filter(
                user=self.authorized,
                author=self.author,
            ).exists()
        )

    def test_auth_can_unfollow(self):
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.authorized,
                author=self.author,
            ).exists()
        )

    def test_new_post_for_follower(self):
        Follow.objects.create(
            user=self.authorized,
            author=self.author,
        )
        count = Post.objects.filter(
            author__following__user=self.authorized).count()
        Post.objects.create(
            text='Текст для фолловеров',
            author=self.author,
        )
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.authorized).count(),
            count + 1)

    def test_no_new_post_for_unfollower(self):
        count = Post.objects.filter(
            author__following__user=self.authorized).count()
        Post.objects.create(
            text='Текст для фолловеров',
            author=self.author,
        )
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.authorized).count(),
            count)


class PaginatorViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGE_TEST_OVERAGE = 3
        cls.user = User.objects.create_user(username='authorized')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(settings.NUMB_PAGIN + cls.PAGE_TEST_OVERAGE):
            cls.post = Post.objects.create(
                author=cls.author,
                group=cls.group,
                text=f'Тестовый текст{[i+1]}'
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        templates_uses_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}
                    ),
        ]
        for reverse_name in templates_uses_paginator:
            cache.clear()
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.NUMB_PAGIN
                                 )

    def test_second_page_contains_ten_records(self):
        templates_uses_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}
                    ),
        ]
        for reverse_name in templates_uses_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.PAGE_TEST_OVERAGE
                                 )

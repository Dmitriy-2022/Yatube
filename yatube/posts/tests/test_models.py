from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(str(self.post), self.post.text[:15],
                         ('Post.__str__ не работает'))
        self.assertEqual(str(self.group), self.group.title,
                         ('Group.__str__ не работает'))

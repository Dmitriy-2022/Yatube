from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image', )
        labels = {
            'text': _('Текст поста'),
            'group': _('Выберите группу')

        }
        help_texts = {
            'text': _('Здесь можно ввести текст поста'),
            'group': _('Здесь можно выбрать группу,'
                       ' к которой будет относиться пост'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        labels = {
            'text': _('Оставьте комментарий'),
        }
        help_texts = {
            'text': _('Здесь можно оставить комментарий к посту'),
        }

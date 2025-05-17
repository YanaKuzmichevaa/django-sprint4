from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .forms import PostForm
from .models import Post, Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class UpdDelCommMixin:
    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['post_id'],
            post__id=self.kwargs['post_id']
        )

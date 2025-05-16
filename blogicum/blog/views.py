from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy

from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView
)

from .forms import PostForm, CommentForm, UserUpdateForm
from .mixins import OnlyAuthorMixin
from .models import Post, Category, Comment
from .query_func import get_optimized_queryset
from .paginate import get_paginator


class ProfileListView(ListView):
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = settings.NUM_OF_POSTS

    @property
    def profile(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs[self.slug_url_kwarg]
        )

    def get_queryset(self):
        queryset = get_optimized_queryset(
            filters=(self.request.user != self.profile),
            annotations=True
        ).filter(author=self.profile)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


def index(request):
    template_name = 'blog/index.html'
    post_list = get_optimized_queryset(filters=True, annotations=True)
    context = get_paginator(request, post_list)
    return render(request, template_name, context)


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, PostMixin, UpdateView
):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class PostDeleteView(
    LoginRequiredMixin, OnlyAuthorMixin, DeleteView
):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


def post_detail(request, post_id):
    template_name = 'blog/detail.html'

    queryset = get_optimized_queryset(filters=False, annotations=False)

    post = get_object_or_404(queryset, pk=post_id)

    is_author = request.user == post.author
    if not is_author:
        queryset_with_filter = get_optimized_queryset(
            filters=True,
            annotations=False
        )
        post = get_object_or_404(queryset_with_filter, pk=post_id)

    comments = post.comments.all().order_by(
        'created_at'
    ).select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_optimized_queryset(
        manager=category.posts,
        filters=True,
        annotations=True
    )
    context = {
        **get_paginator(request, post_list),
        'category': category
    }
    return render(request, template_name, context)


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, UpdateView
):
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['post_id'],
            post_id=self.kwargs['post_id']
        )


class CommentDeleteView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, DeleteView
):
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['post_id'],
            post__id=self.kwargs['post_id']
        )

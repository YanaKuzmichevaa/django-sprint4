from django.utils import timezone
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView
)
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from blog.models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserUpdateForm
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseForbidden


NUM_OF_POSTS = 10


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:password_change_done',
            kwargs={'username': self.request.user.username}
        )


class ProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = NUM_OF_POSTS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        if self.request.user == user:
            post_list = Post.objects.filter(author=user).annotate(
                comment_count=models.Count('comment')
            ).order_by('-pub_date')
        else:
            post_list = get_base_queryset().filter(
                author=user, is_published=True)

        paginator = Paginator(post_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['profile'] = user

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


def get_base_queryset():
    return Post.objects.select_related(
        'category', 'author', 'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=models.Count('comment')).order_by('-pub_date')


def index(request):
    template_name = 'blog/index.html'
    post_list = get_base_queryset()
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
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
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, PostMixin, UpdateView
):
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, PostMixin, DeleteView
):
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


def post_detail(request, post_id):
    template_name = 'blog/detail.html'

    if request.user.is_authenticated:
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        )
    else:
        queryset = get_base_queryset()

    post = get_object_or_404(queryset, pk=post_id)

    if not post.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    if not post.category.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    if post.pub_date > timezone.now() and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    comments = post.comment_set.all().order_by('created_at')
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
    post_list = get_base_queryset().filter(category=category)
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, template_name, context)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("Доступ запрещен")
        return redirect(reverse('login'))


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


class CommentDeleteView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, DeleteView
):
    pk_url_kwarg = 'comment_id'

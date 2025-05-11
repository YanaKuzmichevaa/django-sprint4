from django.urls import path
from django.contrib.auth.views import PasswordChangeDoneView
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'),
    path(
        'profile/<str:username>/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'),
    path(
        'profile/<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile'),
    path(
        'profile/<str:username>/password/',
        views.ProfilePasswordChangeView.as_view(),
        name='password_change'),
    path(
        'profile/<str:username>/password/done/',
        PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    )
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

# socialapp/urls.py

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    RegisterView, ProfileDetailView, PostListCreateView, PostDetailView,
    CommentListCreateView, CommentDetailView, PostLikeView, CommentLikeView,
    FollowUnfollowView, UserSearchView, NewsFeedView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', obtain_auth_token, name='auth-login'),

    path('profiles/<int:user_id>/', ProfileDetailView.as_view(), name='profile-detail'),

    path('posts/', PostListCreateView.as_view(), name='posts-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='posts-detail'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),

    
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comments-list-create'),
    path('comments/<int:comment_id>/', CommentDetailView.as_view(), name='comments-detail'),

    path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('comments/<int:comment_id>/like/', CommentLikeView.as_view(), name='comment-like'),

    path('users/<int:user_id>/follow/', FollowUnfollowView.as_view(), name='user-follow'),

    path('search/users/', UserSearchView.as_view(), name='user-search'),
]
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Profile, Post, Comment
from .serializers import (
    RegisterSerializer, ProfileSerializer, UserSerializer, 
    PostSerializer, CommentSerializer
)

# Authorization and profiles
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user_id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"detail": "Permission denied. You can only edit your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

# personalized feed
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user:
            raise permissions.exceptions.PermissionDenied("You cannot edit this post.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise permissions.exceptions.PermissionDenied("You cannot delete this post.")
        instance.delete()

class NewsFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Fetch posts authored by people the authenticated user follows
        following_profiles = self.request.user.profile.following.all()
        following_users = [profile.user for profile in following_profiles]
        return Post.objects.filter(author__in=following_users).order_by('-created_at')

# comments
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id']).order_by('-created_at')

    def perform_create(self, serializer):
        post_obj = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post_obj)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise permissions.exceptions.PermissionDenied("Access Denied.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise permissions.exceptions.PermissionDenied("Access Denied.")
        instance.delete()

# likes and follows
class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post_obj = get_object_or_404(Post, id=post_id)
        post_obj.post_likes.add(request.user)
        return Response({"detail": "Post liked successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post_obj = get_object_or_404(Post, id=post_id)
        post_obj.post_likes.remove(request.user)
        return Response({"detail": "Like removed successfully."}, status=status.HTTP_200_OK)

class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        comment_obj = get_object_or_404(Comment, id=comment_id)
        comment_obj.comment_likes.add(request.user)
        return Response({"detail": "Comment liked successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        comment_obj = get_object_or_404(Comment, id=comment_id)
        comment_obj.comment_likes.remove(request.user)
        return Response({"detail": "Like removed from comment."}, status=status.HTTP_200_OK)

class FollowUnfollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.profile.following.add(target_user.profile)
        return Response({"detail": f"Now following {target_user.username}."}, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        request.user.profile.following.remove(target_user.profile)
        return Response({"detail": f"Unfollowed {target_user.username} successfully."}, status=status.HTTP_200_OK)

# search
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return User.objects.filter(username__icontains=query)
        return User.objects.none()
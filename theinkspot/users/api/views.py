from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .serializers import UserSerializer, FollowingSerializer, FollowerSerializer

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FollowersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FollowerSerializer(user.followers.all(), many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FollowingsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FollowingSerializer(user.following.all(), many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        followed_username = request.data.get("followed_username")
        try:
            user = User.objects.get(username=username)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"detail": "User not found"})
        user_follow = UserFollow.objects.create(follower_user=request.user, followed_user=user)
        user_follow.save()
        return Response(status=status.HTTP_200_OK)


class UnfollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        user = User.objects.get(username=username)
        UserFollow.objects.filter(follower_user=request.user, followed_user=user).delete()
        return Response(status=status.HTTP_200_OK)

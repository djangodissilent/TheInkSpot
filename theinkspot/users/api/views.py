from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView


from .serializers import UserSerializer

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


class FollowUser(APIView):
    def post(self, request, format=None):
        username = request.data.get("username")
        if username is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_follow = UserFollowing(follower_user=request.user, followed_user=user)
        try:
            user_follow.save()
        except ValueError as ve:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": ve.args[0]})

        return Response(status=status.HTTP_201_CREATED)


class UnfollowUser(APIView):
    def post(self, request, format=None):
        username = request.data.get("username")
        if username is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            user_follow = UserFollowing.objects.filter(follower_user=request.user, followed_user=user)

        except UserFollowing.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user_follow.delete()
        except ValueError as ve:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": ve.args[0]})

        return Response(status=status.HTTP_201_CREATED)

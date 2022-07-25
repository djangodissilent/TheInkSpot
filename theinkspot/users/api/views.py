# from email.message import _PayloadType
import jwt
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from config.settings.local import SECRET_KEY

from .serializers import RegisterUser

# from django.core import mail


User = get_user_model()


class RegisterUsers(generics.GenericAPIView):

    serializer_class = RegisterUser

    def post(self, request):

        user = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        # this part needs to move to another flow https://oyasr.atlassian.net/browse/INK-40
        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user).access_token
        current_site = "0.0.0.0:8000"
        relative_link = reverse("api:verify-email")
        absurl = "http://" + current_site + relative_link + "?token=" + str(token)
        email_body = (
            "Hi "
            + user.name.split(" ")[0]
            + ",\n"
            + "Thank you for registering with us, Please use the link below to verify your email address \n"
            + absurl
        )
        email_subject = "Verify your email address"

        email = EmailMessage(subject=email_subject, body=email_body, to=[user.email])
        email.send()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            Payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=Payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {"email": "Successfully Activated"}, status=status.HTTP_200_OK
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )

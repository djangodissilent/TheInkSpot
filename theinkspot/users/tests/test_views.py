import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from theinkspot.users.forms import UserAdminChangeForm
from theinkspot.users.models import User
from theinkspot.users.tests.factories import UserFactory
from theinkspot.users.views import UserRedirectView, UserUpdateView, user_detail_view
from rest_framework.test import APIClient
from theinkspot.users.api.views import  RegisterUsers,VerifyEmail
from django.core import mail
from unittest.mock import MagicMock, call
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from config.settings.local import SECRET_KEY
from django.core.mail import EmailMessage
# import re


pytestmark = pytest.mark.django_db
client = APIClient()

class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_success_url() == f"/users/{user.username}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = []
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == ["Information successfully updated"]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request

        assert view.get_redirect_url() == f"/users/{user.username}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()

        response = user_detail_view(request, username=user.username)

        assert response.status_code == 200

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()

        response = user_detail_view(request, username=user.username)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        assert response.url == f"{login_url}?next=/fake-url/"



@pytest.mark.django_db
class TestRegisterView:
    def test_register_user_valid_data(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
     }
        response =client.post('/api/users/register/', data)
        payload = response.data
        assert response.status_code == 201
        assert payload["name"]== data["name"]
        assert payload["email"]== data["email"]
        user = User.objects.filter(username='nancy_farid_1').first()
        assert user is not None
        assert user.email == 'nancyfarid1@gmail.com'  

    def test_register_user_with_empty_name(self):
        data={
        "name":"",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }

        response =client.post('/api/users/register/', data)
        assert response.status_code == 400

    def test_register_user_with_name_len_less_than_8(self):
        data={
        "name":"nancy",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400        

    def test_register_user_with_empty_username(self):
        data={
        "name":"nancy farid",
        "username":"",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }

        response =client.post('/api/users/register/', data)
        assert response.status_code == 400

    def test_register_user_with_username_len_less_than_8(self):
        data={
        "name":"nancy farid",
        "username":"nancy_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400       

    def test_register_user_with_username_already_exists(self,user):
        data={
        "name":"nancy farid",
        "username":"username",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        # user= User.objects.create_user("nancy farid","nancy_farid_1","nancy@gmail.com", "Nan123456789555Far")
        # if (User.objects.filter(username=data["username"]).first()):
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400                

    def test_register_empty_email(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400
    
    def test_register_user_with_invalid_email_format(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"nancyfa.o",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400   

    def test_register_user_with_email_already_exists(self,user):
        data={
        "name":"nancy",
        "username":"nancy_farid_1",
        "email":"test@email.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Nan123456789555Far"
        }
        # user= User.objects.create_user("nancy farid","nancy_farid","nancyfarid1@gmail.com", "Nan123456789555Far")
        # if (User.objects.filter(email=data["email"]).first()):
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400           

    def test_register_user_with_no_password(self):
        data={
        "name":"nancy",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400

    def test_register_user_with_no_password_confirmation(self):
        data={
        "name":"nancy",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": ""
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400            
    
    def test_register_user_with_password_min_len(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456",
        "password_confirmation": "Nan123456"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400 

    def test_register_user_with_password_max_len(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":40*"Na12",
        "password_confirmation": "Nan123456789555Far"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400         

    def test_register_user_diffrant_passwords(self):
        data={
        "name":"nancy",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"Nan123456789555Far",
        "password_confirmation": "Far123456789555Nan"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400
    
    def test_register_user_with_invalid_passwords(self):
        data={
        "name":"nancy farid",
        "username":"nancy_farid_1",
        "email":"nancyfarid1@gmail.com",
        "password":"123456789555",
        "password_confirmation": "Far123456789555Nan"
        }
        response =client.post('/api/users/register/', data)
        assert response.status_code == 400

    # def test_send_mail(self):
    #     email= EmailMessage(
    #         'Example subject here',
    #         'Here is the message body.',
    #         ['to@example.com']
    #     )
    #     email.send()
    #     assert len(mail.outbox) == 1, "Inbox is not empty"
    #     assert mail.outbox[0].subject == 'Example subject here'
    #     assert mail.outbox[0].to == ['to@example.com']

    # def test_no_email_sent(self):
    #     email= EmailMessage(
    #         'Example subject here',
    #         'Here is the message body.',
    #         'from@example.com',
    #         ['']
    #     )
    #     email.send()
    #     assert len(mail.outbox)== 0  


class TestVerificatinMailView:
    @pytest.mark.django_db
    def test_successfull_account_activatin(self,user):
        token = RefreshToken.for_user(user).access_token
        current_site = "0.0.0.0:8000"
        relative_link = reverse("api:verify-email")
        absurl = "http://" + current_site + relative_link + "?token=" + str(token)
        request =client.get(absurl)
        print(request.data)
        assert request.status_code == 200
        assert user.is_verified == True
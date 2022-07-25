import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from theinkspot.users.models import User

pytestmark = pytest.mark.django_db
client = APIClient()


@pytest.mark.django_db
class TestRegisterView:
    def test_register_user_valid_data(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        payload = response.data
        assert response.status_code == 201
        assert payload["name"] == data["name"]
        assert payload["email"] == data["email"]
        user = User.objects.filter(username="nancy_farid_1").first()
        assert user is not None
        assert user.email == "nancyfarid1@gmail.com"

    def test_register_user_with_empty_name(self):
        data = {
            "name": "",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }

        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_name_len_less_than_8(self):
        data = {
            "name": "nancy",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_empty_username(self):
        data = {
            "name": "nancy farid",
            "username": "",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }

        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_username_len_less_than_8(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_username_already_exists(self, user):
        data = {
            "name": "nancy farid",
            "username": "username",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        # user= User.objects.create_user("nancy farid","nancy_farid_1","nancy@gmail.com", "Nan123456789555Far")
        # if (User.objects.filter(username=data["username"]).first()):
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_empty_email(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_invalid_email_format(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "nancyfa.o",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_email_already_exists(self, user):
        data = {
            "name": "nancy",
            "username": "nancy_farid_1",
            "email": "test@email.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Nan123456789555Far",
        }
        # user= User.objects.create_user("nancy farid","nancy_farid","nancyfarid1@gmail.com", "Nan123456789555Far")
        # if (User.objects.filter(email=data["email"]).first()):
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_no_password(self):
        data = {
            "name": "nancy",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_no_password_confirmation(self):
        data = {
            "name": "nancy",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_password_min_len(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456",
            "password_confirmation": "Nan123456",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_password_max_len(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": 40 * "Na12",
            "password_confirmation": "Nan123456789555Far",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_diffrant_passwords(self):
        data = {
            "name": "nancy",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "Nan123456789555Far",
            "password_confirmation": "Far123456789555Nan",
        }
        response = client.post("/api/users/register/", data)
        assert response.status_code == 400

    def test_register_user_with_invalid_passwords(self):
        data = {
            "name": "nancy farid",
            "username": "nancy_farid_1",
            "email": "nancyfarid1@gmail.com",
            "password": "123456789555",
            "password_confirmation": "Far123456789555Nan",
        }
        response = client.post("/api/users/register/", data)
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
    def test_successfull_account_activatin(self, user):
        token = RefreshToken.for_user(user).access_token
        current_site = "0.0.0.0:8000"
        relative_link = reverse("api:verify-email")
        absurl = "http://" + current_site + relative_link + "?token=" + str(token)
        request = client.get(absurl)
        print(request.data)
        assert request.status_code == 200
        assert user.is_verified is True

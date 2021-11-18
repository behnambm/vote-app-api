from unittest import mock

from django.db.utils import IntegrityError
from django.test import Client, SimpleTestCase, TestCase
from django.urls import resolve, reverse

from users.api import CheckVerificationCodeView, EmailView
from users.models import Emails
from users.tasks import send_verification_code
from users.utils import (
    generate_verification_code,
    is_code_correct,
    is_code_in_redis,
    set_verification_code,
)


class TestUrls(SimpleTestCase):
    def test_user_email_is_resolved(self):
        url = reverse("send-verification-code")
        self.assertEqual(resolve(url).func.view_class, EmailView)

    def test_verification_code_check_is_resolved(self):
        url = reverse("check-verification-code")
        self.assertEqual(
            resolve(url).func.view_class, CheckVerificationCodeView
        )


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.send_verification_code_url = reverse("send-verification-code")
        self.check_verification_code_url = reverse("check-verification-code")

    def test_verification_code_POST_no_data_provided(self):
        response = self.client.post(self.send_verification_code_url)
        print(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("email")[0], "This field is required."
        )

    @mock.patch("users.utils.redis.StrictRedis.get", return_value=False)
    @mock.patch("users.api.is_code_in_redis", return_value=False)
    def test_verification_code_POST_successful(
        self, mock_is_code_in_redis, mock_r_get
    ):
        response = self.client.post(
            self.send_verification_code_url, data={"email": "test@email.com"}
        )
        self.assertTrue(mock_is_code_in_redis.called)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please check your inbox")

    @mock.patch("users.api.is_code_in_redis", return_value=True)
    def test_verification_code_POST_wait_120_sec(self, mock_is_code_in_redis):
        response = self.client.post(
            self.send_verification_code_url, data={"email": "test2@email.com"}
        )
        self.assertTrue(mock_is_code_in_redis.called)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            response.json().get("detail"), "please wait 120 seconds"
        )

    @mock.patch("users.tasks.send_mail")
    def test_send_verification_code_func(self, mock_send_mail):
        ret = send_verification_code(email="test@email.com", code="234123")
        self.assertTrue(mock_send_mail.called)

    def test_check_verification_POST_no_data(self):
        response = self.client.post(self.check_verification_code_url)
        self.assertEqual(response.status_code, 400)

    def test_check_verification_POST_invalid_email(self):
        response = self.client.post(
            self.check_verification_code_url, data={"email": "not_an_email"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("email")[0], "Enter a valid email address."
        )

    def test_check_verification_POST_invalid_non_digit_code(self):
        response = self.client.post(
            self.check_verification_code_url, data={"code": "abcdef"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("code")[0], "Only digits are allowed"
        )

    def test_check_verification_POST_invalid_short_code(self):
        response = self.client.post(
            self.check_verification_code_url, data={"code": "12345"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("code")[0], "Code is only 6 digits long"
        )

    def test_check_verification_POST_invalid_long_code(self):
        response = self.client.post(
            self.check_verification_code_url, data={"code": "1234567"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("code")[0], "Code is only 6 digits long"
        )

    @mock.patch("users.api.is_code_correct", return_value=False)
    def test_check_verification_POST_not_valid_code(self, mock_is_code_correct):
        response = self.client.post(
            self.check_verification_code_url,
            data={"email": "test@email.com", "code": "123456"},
        )
        self.assertTrue(mock_is_code_correct.called)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Code is not correct")

    @mock.patch("users.api.is_code_correct", return_value=True)
    def test_check_verification_POST_valid_code(self, mock_is_code_correct):
        response = self.client.post(
            self.check_verification_code_url,
            data={"email": "test@email.com", "code": "123456"},
        )
        self.assertTrue(mock_is_code_correct.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("detail"), "successful")

        email_obj = Emails.objects.get(email="test@email.com")
        self.assertTrue(email_obj.is_active)


class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email_obj = Emails.objects.create(
            email="test@email.com", is_active=True
        )

    def test_email_field__uniqueness(self):
        with self.assertRaises(IntegrityError):
            Emails.objects.create(email="test@email.com")

    def test_email_model_str(self):
        self.assertEqual(
            str(self.email_obj),
            f"{self.email_obj.email} (active: {self.email_obj.is_active})",
        )


class TestUtils(SimpleTestCase):
    def test_generate_verification_code_length(self):
        self.assertEqual(len(generate_verification_code()), 6)

    def test_generate_verification_code_is_digit(self):
        self.assertTrue(generate_verification_code().isdigit())

    def test_generate_verification_code_returns_str(self):
        self.assertTrue(type(generate_verification_code()) == str)

    @mock.patch("users.utils.redis.StrictRedis.set", return_value=True)
    def test_set_verification_code(self, mock_set_verification_code):
        ret = set_verification_code("test@email.com", "123456")

        self.assertTrue(mock_set_verification_code.called)
        self.assertTrue(ret)

    @mock.patch("users.utils.redis.StrictRedis.get", return_value=True)
    def test_is_code_in_redis(self, mock_is_code_in_redis):
        self.assertTrue(is_code_in_redis("test@email.com"))
        self.assertTrue(mock_is_code_in_redis.called)

    @mock.patch("users.utils.redis.StrictRedis.get", return_value=b"123123")
    def test_is_code_correct(self, mock_is_code_correct):
        self.assertTrue(is_code_correct("test@email.com", 123123))
        self.assertTrue(mock_is_code_correct.called)

    @mock.patch("users.utils.redis.StrictRedis.get", return_value="123123")
    def test_is_code_correct_not_working_with_str_return_from_redis(
        self, mock_is_code_correct
    ):
        # returns false because the data that is fetched from redis
        # should be in byte type.
        # if you call `.decode()` on it, it will raise an AttributeError

        self.assertFalse(is_code_correct("test@gmail.com", "123123"))
        self.assertTrue(mock_is_code_correct.called)

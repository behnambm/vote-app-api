import json

from django.db.utils import IntegrityError
from django.test import SimpleTestCase, TestCase
from django.test.client import Client
from django.urls import resolve, reverse
from django.utils.text import slugify
from users.models import Emails

from .api import VotesView
from .models import Voters, Votes


class TestUrls(SimpleTestCase):
    def setUp(self):
        self.vote_url = reverse("vote")

    def test_vote_url(self):
        self.assertEqual(resolve(self.vote_url).func.view_class, VotesView)


class TestViews(TestCase):
    def setUp(self):
        self.vote_url = reverse("vote")
        self.client = Client()

    def test_no_votes(self):
        response = self.client.get(self.vote_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_vote_PUT_no_data(self):
        response = self.client.put(self.vote_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("email")[0], "This field is required."
        )
        self.assertEqual(
            response.json().get("user_choice")[0], "This field is required."
        )
        self.assertEqual(
            response.json().get("vote_id")[0], "This field is required."
        )

    def test_vote_PUT_invalid_email(self):
        response = self.client.put(
            self.vote_url,
            data=json.dumps({"email": "not_a_valid_email"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("email")[0], "Enter a valid email address."
        )

    def test_vote_PUT_email_does_not_exist(self):
        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "dogs",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get("detail"), "email not found")

    def test_vote_PUT_email_does_not_have_permission(self):
        Emails.objects.create(email="test@email.com", is_active=False)

        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "dogs",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "email not activated")

    def test_vote_PUT_vote_does_not_exist(self):
        Emails.objects.create(email="test@email.com", is_active=True)

        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "dogs",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get("detail"), "vote does not exist")

    def test_vote_PUT_invalid_user_choice(self):
        Emails.objects.create(email="test@email.com", is_active=True)
        Votes.objects.create(
            title="Dogs vs Cats",
            description="testing vote",
            first_option="dogs",
            second_option="cats",
        )

        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "invalid choice",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("detail"),
            "'invalid choice' is not a valid option",
        )

    def test_vote_PUT_create_new_vote(self):
        Emails.objects.create(email="test@email.com", is_active=True)
        Votes.objects.create(
            title="Dogs vs Cats",
            description="testing vote",
            first_option="dogs",
            second_option="cats",
        )

        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "dogs",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("detail"),
            "successful",
        )
        self.assertEqual(
            response.json().get("user_choice"),
            "dogs",
        )

    def test_vote_PUT_update_vote(self):
        email_obj = Emails.objects.create(
            email="test@email.com", is_active=True
        )
        a_vote = Votes.objects.create(
            title="Dogs vs Cats",
            description="testing vote",
            first_option="dogs",
            second_option="cats",
        )
        Voters.objects.create(vote=a_vote, voter=email_obj, user_choice="cats")

        response = self.client.put(
            self.vote_url,
            data=json.dumps(
                {
                    "email": "test@email.com",
                    "user_choice": "dogs",
                    "vote_id": 1,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("detail"),
            "successful",
        )
        self.assertEqual(
            response.json().get("user_choice"),
            "dogs",
        )


class TestModels(TestCase):
    def setUp(self):
        self.vote = Votes.objects.create(
            title="some title for a vote",
            description="some description",
            first_option="option a",
            second_option="option b",
        )
        self.email_obj = Emails.objects.create(
            email="test@email.com", is_active=True
        )

    def test_vote_is_assigned_slug_on_creation(self):
        self.assertEqual(self.vote.slug, slugify("some title for a vote"))

    def test_vote_model_str(self):
        self.assertEqual(
            str(self.vote),
            f"{self.vote.title}({self.vote.first_option}, {self.vote.second_option})",
        )

    def test_voter_model_str(self):
        voter_obj = Voters.objects.create(
            vote=self.vote, voter=self.email_obj, user_choice="option a"
        )
        self.assertEqual(
            str(voter_obj),
            f"{self.email_obj.email} ({voter_obj.user_choice})",
        )

    def test_voter_models_unique_constraint(self):
        email_obj = Emails.objects.create(
            email="test1@email.com", is_active=True
        )

        Voters.objects.create(
            vote=self.vote, voter=email_obj, user_choice="cats"
        )

        with self.assertRaises(IntegrityError):
            Voters.objects.create(
                vote=self.vote, voter=email_obj, user_choice="option b"
            )

    def test_voter_models_user_choice_max_length(self):
        self.assertEqual(Voters._meta.get_field("user_choice").max_length, 256)

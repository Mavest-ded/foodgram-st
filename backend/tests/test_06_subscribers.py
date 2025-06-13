import pytest
from django.urls import reverse_lazy
from rest_framework import status
from tests.utils import check_pagination


@pytest.mark.django_db
@pytest.mark.usefixtures('recipes')
class TestSubscribers:
    URL_SUBSCRIBERS = reverse_lazy('api:users-subscriptions')

    @staticmethod
    def url_subscribe_detail(pk):
        return reverse_lazy('api:users-subscribe', args=[pk])

    @pytest.mark.parametrize(
        'current_client, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                status.HTTP_200_OK,
            ),
            (pytest.lazy_fixture('user_client'), status.HTTP_401_UNAUTHORIZED),
        ),
    )
    def test_01_get_subscribers(
        self, current_client, expected_status, admin_user
    ):
        recipes_limit = 1
        current_client.post(self.url_subscribe_detail(admin_user.pk))
        response = current_client.get(self.URL_SUBSCRIBERS)
        assert response.status_code == expected_status

        if expected_status != status.HTTP_200_OK:
            return

        response = current_client.get(
            self.URL_SUBSCRIBERS + f'?recipes_limit={recipes_limit}'
        )

        json_response = response.json()
        check_pagination(json_response)
        assert len(json_response['results']) > 0, json_response
        json_recipes = json_response['results'][0]['recipes']
        assert len(json_recipes) == recipes_limit

    @pytest.mark.parametrize(
        'current_client, current_user, user2, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                pytest.lazy_fixture('user'),
                pytest.lazy_fixture('admin_user'),
                status.HTTP_201_CREATED,
            ),
            (
                pytest.lazy_fixture('admin_client'),
                pytest.lazy_fixture('admin_user'),
                pytest.lazy_fixture('user'),
                status.HTTP_401_UNAUTHORIZED,
            ),
        ),
    )
    def test_02_subscribe(
        self, current_client, current_user, user2, expected_status
    ):
        response = current_client.post(self.url_subscribe_detail(user2.pk))
        assert response.status_code == expected_status, response.json()

        if expected_status != status.HTTP_201_CREATED:
            return

        bad_response = current_client.post(self.url_subscribe_detail(user2.pk))
        assert (
            bad_response.status_code == status.HTTP_400_BAD_REQUEST
        ), response.json()

        bad_response = current_client.post(
            self.url_subscribe_detail(current_user.pk)
        )
        assert bad_response.status_code == status.HTTP_400_BAD_REQUEST

        json_response = response.json()

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

        for field in fields:
            assert field in json_response, f'Field {field} not in response'

        recipe_fields = ('id', 'name', 'image', 'cooking_time')
        recipes_json = json_response['recipes'][0]
        for field in recipe_fields:
            assert field in recipes_json, f'Field {field} not in `recipes`'

        assert len(json_response) == len(
            fields
        ), f'Expected {len(fields)} fields, got {len(json_response)}'

    def test_02_subscribe_with_query(self, user_client_with_token, admin_user):
        recipes_limit = 1
        response = user_client_with_token.post(
            self.url_subscribe_detail(admin_user.id)
            + f'?recipes_limit={recipes_limit}'
        )
        json_response = response.json()['recipes']
        assert (
            len(json_response) == recipes_limit
        ), f'Expected {recipes_limit} response, got {len(json_response)}'

    @pytest.mark.parametrize(
        'current_client, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                status.HTTP_204_NO_CONTENT,
            ),
            (
                pytest.lazy_fixture('user_client'),
                status.HTTP_401_UNAUTHORIZED,
            ),
        ),
    )
    def test_03_delete_subscriber(
        self, current_client, expected_status, admin_user
    ):
        current_client.post(self.url_subscribe_detail(admin_user.pk))
        response = current_client.delete(
            self.url_subscribe_detail(admin_user.pk)
        )
        assert response.status_code == expected_status

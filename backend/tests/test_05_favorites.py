from http import HTTPStatus

import pytest
from django.urls import reverse_lazy
from tests.utils import check_author_recipe


@pytest.mark.django_db
@pytest.mark.usefixtures('recipes')
class TestFavorites:
    @staticmethod
    def url_favorite(pk):
        return reverse_lazy('api:recipe-favorite', args=[pk])

    @pytest.mark.parametrize(
        'current_client, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                HTTPStatus.CREATED,
            ),
            (pytest.lazy_fixture('client'), HTTPStatus.UNAUTHORIZED),
        ),
    )
    def test_01_favorites(self, current_client, expected_status):
        check_author_recipe(current_client, expected_status, self.url_favorite)

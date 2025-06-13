from http import HTTPStatus

import pytest
from rest_framework.reverse import reverse_lazy

from recipes.models import Tag


TAG_FIELDS = (
    'id',
    'name',
    'slug',
)


@pytest.mark.django_db
@pytest.mark.usefixtures('tags')
class Test02Tags:
    URL_TAGS = reverse_lazy('api:tag-list')
    URL_TAG_DETAIL = reverse_lazy('api:tag-detail', kwargs={'pk': 1})

    @pytest.mark.parametrize(
        'expected_client',
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('user_client'),
            pytest.lazy_fixture('client'),
        ),
    )
    def test_02_get_tags(self, expected_client):
        response = expected_client.get(self.URL_TAGS)

        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), list)

        json_response = response.json()[0]
        assert len(json_response) == len(
            TAG_FIELDS
        ), f'Expected {len(TAG_FIELDS)} tags, got {len(json_response)}'
        for field in TAG_FIELDS:
            assert (
                field in json_response
            ), f'Response does not contain field {field!r}'

    @pytest.mark.parametrize(
        'expected_client',
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('user_client'),
            pytest.lazy_fixture('client'),
        ),
    )
    def test_02_get_tag(self, expected_client):
        response = expected_client.get(self.URL_TAG_DETAIL)

        assert response.status_code == HTTPStatus.OK

        json_response = response.json()
        assert len(json_response) == len(
            TAG_FIELDS
        ), f'Expected {len(TAG_FIELDS)} tags, got {len(json_response)}'
        for field in TAG_FIELDS:
            assert (
                field in json_response
            ), f'Response does not contain field {field!r}'

    def test_02_bad_tag(self, client):
        bad_id = Tag.objects.last().id + 1
        response = client.get(
            reverse_lazy('api:tag-detail', kwargs={'pk': bad_id})
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

import pytest
from django.urls import reverse_lazy
from rest_framework import status
from tests.utils import check_author_recipe


@pytest.mark.django_db
@pytest.mark.usefixtures('recipes')
class Test04Cart:
    URL_CART = reverse_lazy('api:recipe-download')

    @staticmethod
    def url_cart(pk):
        return reverse_lazy('api:recipe-shopping-cart', args=[pk])

    @pytest.mark.parametrize(
        'current_client, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                status.HTTP_200_OK,
            ),
            # (
            #     pytest.lazy_fixture('user_client'),
            #     status.HTTP_401_UNAUTHORIZED,
            # ),
        ),
    )
    def test_01_get_cart_list(self, current_client, expected_status):
        for i in range(1, 10):
            current_client.post(self.url_cart(i))
        response = current_client.get(self.URL_CART)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'current_client, expected_status',
        (
            (
                pytest.lazy_fixture('user_client_with_token'),
                status.HTTP_201_CREATED,
            ),
            (pytest.lazy_fixture('client'), status.HTTP_401_UNAUTHORIZED),
        ),
    )
    def test_02_add_cart(self, current_client, expected_status):
        check_author_recipe(current_client, expected_status, self.url_cart)

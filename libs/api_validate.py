from typing import Any, Dict
import requests, logging
logger = logging.getLogger(__name__)


class APIValidate:

    def __init__(self, max_response_time: int = 1000):
        self.max_response_time = max_response_time

    def assert_status_code(self, response: requests.Response, expected: int = 200):
        """ Validate HTTP status code """
        logger.info(f"\nResponse status code: {response.status_code}")
        assert response.status_code == expected, \
            f"Status code mismatch.\nExpected: {expected}\nActual: {response.status_code}"

    def assert_field_exists(self, response: requests.Response, field: str):
        """ Validate field/property exists in response """
        res_body = response.json()
        assert field in res_body, f"Field not found.\nExpected: {field}\nActual: {list(res_body.keys())}"

    def assert_token_received(self, response: requests.Response, api_client):
        """ Validate token is received and stored in api_client """
        self.assert_field_exists(response, "token")
        assert api_client.token is not None, f"Token not stored.\nExpected: not None\nActual: {api_client.token}"
        assert len(api_client.token) >= 1, \
            f"Token is empty.\nExpected: len(token) >= 1\nActual: {len(api_client.token)}"

    def assert_test_response(self, response: requests.Response, expected_text: str):
        """ Validate test response """
        assert expected_text in response.text, \
            f"Text mismatch.\nExpected: '{expected_text}'\nActual: '{response.text!r}'"

    def assert_booking_created(self, response: requests.Response, api_client):
        """ Validate booking is created and stored in api_client """
        self.assert_field_exists(response, "bookingid")
        self.assert_field_exists(response, "booking")
        assert api_client.booking_id is not None, \
            f"booking_id not stored.\nExpected: not None\nActual: {api_client.booking_id}"
        assert api_client.booking_data is not None, \
            f"booking_data not stored.\nExpected: not None\nActual: {api_client.booking_data}"

    def assert_booking_data_matches(self, response: requests.Response, expected_data: Dict[str, Any]):
        """ Validate all booking fields match expected data. Used for CREATE, GET, UPDATE, PATCH operations """
        res_body = response.json()
        actual_data = res_body.get("booking", res_body)
        assert actual_data == expected_data, f"Booking data mismatch.\nExpected: {expected_data}\nActual: {actual_data}"




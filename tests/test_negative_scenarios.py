import logging
import os

import pytest
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables (*.env)
load_dotenv()


@pytest.mark.negative_scenarios
@pytest.mark.usefixtures("health_check")
class TestNegativeScenarios:
    """ Negative-path checks not covered by the chained CRUD/auth workflows: invalid credentials,
    a nonexistent/malformed booking ID on every method, and a syntactically-invalid (not just
    missing/expired) auth token. Self-contained - doesn't depend on test_workflow_1/2/3 having
    run first, and establishes its own valid token partway through for the steps that need one. """

    def test_create_token_with_invalid_credentials(self, api_client, api_validate):
        """Verify authenticating with wrong credentials returns 200 with a 'Bad credentials' reason, not a token."""
        logger.info("Given wrong username/password\n\tWhen I request an authentication token"
                    "\n\tThen I receive 200 with a 'Bad credentials' reason, not a token\n")

        # Request POST to create token with deliberately wrong credentials
        response = api_client.create_token(username="wrong_user", password="wrong_password")
        logger.info(f"CreateToken response: {response.json()}")

        # Verify status code -> 200 (the API returns 200 even for invalid credentials, not 401/403)
        api_validate.assert_status_code(response, 200)

        # Verify the response carries a rejection reason instead of a token
        res_body = response.json()
        assert "token" not in res_body, f"Expected no token for invalid credentials.\nActual: {res_body}"
        assert res_body.get("reason") == "Bad credentials", f"Unexpected reason.\nActual: {res_body}"


    def test_create_valid_token_for_remaining_tests(self, api_client, api_validate):
        """Establish a real, valid token - this class doesn't depend on another file having run first."""
        logger.info("Given valid authentication credentials\n\tWhen I request an authentication token"
                    "\n\tThen I receive a valid token, replacing the invalid attempt above\n")

        # Request POST to create token with valid credentials
        response = api_client.create_token(username=os.getenv("USER"),
                                           password=os.getenv("PASSWORD"))
        logger.info(f"CreateToken response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify token is in response body, then store it and check if len(token) >= 1
        api_validate.assert_token_received(response, api_client)


    def test_get_booking_by_nonexistent_id(self, api_client, api_validate):
        """Verify fetching a booking ID that doesn't exist returns 404, not a crash or an empty 200."""
        logger.info("Given a booking ID that doesn't exist\n\tWhen I retrieve that booking"
                    "\n\tThen I receive 404 Not Found\n")

        # Request GET for a booking ID that has never been assigned
        response = api_client.get_booking_by_id(booking_id=999999999)
        logger.info(f"GetBooking response: {response.text}")

        # Verify status code -> 404 Not Found
        api_validate.assert_status_code(response, 404)

        # Verify response body -> 'Not Found'
        api_validate.assert_test_response(response, "Not Found")


    def test_get_booking_by_malformed_id(self, api_client, api_validate):
        """Verify fetching a non-numeric booking ID returns 404 rather than a 500 or an unhandled error."""
        logger.info("Given a non-numeric booking ID\n\tWhen I retrieve that booking"
                    "\n\tThen I receive 404 Not Found\n")

        # Request GET with a non-numeric booking ID
        response = api_client.get_booking_by_id(booking_id="abc123")
        logger.info(f"GetBooking response: {response.text}")

        # Verify status code -> 404 Not Found
        api_validate.assert_status_code(response, 404)

        # Verify response body -> 'Not Found'
        api_validate.assert_test_response(response, "Not Found")


    def test_update_booking_nonexistent_id(self, api_client, api_validate):
        """Verify PUT to a booking ID that doesn't exist returns 405, not a silently-created resource."""
        logger.info("Given a booking ID that doesn't exist\n\tWhen I attempt to fully update that booking"
                    "\n\tThen I receive 405 Method Not Allowed\n")

        # Define booking data for the request body - content doesn't matter, the ID is what's under test
        update_data = {"firstname": "Ghost", "lastname": "Booking", "totalprice": 1, "depositpaid": True,
                       "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}, "additionalneeds": "None"}

        # Request PUT to a booking ID that has never been assigned
        response = api_client.update_booking(booking_id=999999999, booking_data=update_data)
        logger.info(f"UpdateBooking response: {response.text}")

        # Verify status code -> 405 Method Not Allowed
        api_validate.assert_status_code(response, 405)

        # Verify response body -> 'Method Not Allowed'
        api_validate.assert_test_response(response, "Method Not Allowed")


    def test_partial_update_booking_nonexistent_id(self, api_client, api_validate):
        """Verify PATCH to a booking ID that doesn't exist returns 405, not a silently-created resource."""
        logger.info("Given a booking ID that doesn't exist\n\tWhen I attempt to partially update that booking"
                    "\n\tThen I receive 405 Method Not Allowed\n")

        # Request PATCH to a booking ID that has never been assigned
        response = api_client.partial_update_booking(booking_id=999999999, booking_data={"firstname": "Ghost"})
        logger.info(f"PartialUpdateBooking response: {response.text}")

        # Verify status code -> 405 Method Not Allowed
        api_validate.assert_status_code(response, 405)

        # Verify response body -> 'Method Not Allowed'
        api_validate.assert_test_response(response, "Method Not Allowed")


    def test_delete_booking_nonexistent_id(self, api_client, api_validate):
        """Verify DELETE on a booking ID that doesn't exist returns 405, not a silent success."""
        logger.info("Given a booking ID that doesn't exist\n\tWhen I attempt to delete that booking"
                    "\n\tThen I receive 405 Method Not Allowed\n")

        # Request DELETE for a booking ID that has never been assigned
        response = api_client.delete_booking(booking_id=999999999)
        logger.info(f"DeleteBooking response: {response.text}")

        # Verify status code -> 405 Method Not Allowed
        api_validate.assert_status_code(response, 405)

        # Verify response body -> 'Method Not Allowed'
        api_validate.assert_test_response(response, "Method Not Allowed")


    def test_update_booking_with_invalid_token(self, api_client, api_validate):
        """Verify PUT with a syntactically-invalid token is rejected with 403, same as a missing/expired one."""
        logger.info("Given a booking created for this test and a syntactically-invalid auth token"
                    "\n\tWhen I attempt to fully update that booking\n\tThen I receive 403 Forbidden\n")

        # Create a throwaway booking of our own for this test, so it doesn't depend on any
        # other test's booking still existing
        booking_data = {"firstname": "Throwaway", "lastname": "Booking", "totalprice": 1, "depositpaid": True,
                        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}, "additionalneeds": "None"}
        create_response = api_client.create_booking(booking_data=booking_data)
        api_validate.assert_status_code(create_response, 200)
        throwaway_booking_id = create_response.json()["bookingid"]

        # Request PUT with a token that was never issued by the API at all
        update_data = {**booking_data, "firstname": "Should Not Apply"}
        response = api_client.update_booking_invalid_token(booking_id=throwaway_booking_id, booking_data=update_data)
        logger.info(f"UpdateBooking response: {response.text}")

        # Verify status code -> 403 Forbidden
        api_validate.assert_status_code(response, 403)

        # Verify response body -> 'Forbidden'
        api_validate.assert_test_response(response, "Forbidden")

        # Cleanup: delete the throwaway booking (the invalid-token attempt above never touched
        # api_client.token, so the real one from earlier in this class is still valid here)
        cleanup_response = api_client.delete_booking(booking_id=throwaway_booking_id)
        api_validate.assert_status_code(cleanup_response, 201)

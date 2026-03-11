import pytest, responses, random, os, names, logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

# Load environment variables (*.env)
load_dotenv()


@pytest.mark.workflow2
@pytest.mark.usefixtures("health_check")
class TestWorkFlow2:
    """ Workflow 2: Authentication Token Lifecycle """

    def test_create_token(self, api_client):
        logger.info(f"\nStep 1: Given valid authentication credentials\n\tWhen I request an authentication token"
                    f"\n\tThen I receive a valid token")

        # Request POST to create token
        response = api_client.create_token(username=os.getenv("USER"),
                                           password=os.getenv("PASSWORD"))

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nCreateToken response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body contains 'token', store it -> received and stored
        assert "token" in res_body
        assert api_client.token is not None


    def test_create_booking(self, api_client):
        logger.info(f"\nStep 2: When I create a new booking (no auth required)"
                    f"\n\tThen the booking is created with unique ID")

        # Define request body with booking details
        booking_data = {"firstname": names.get_first_name(),
                        "lastname": names.get_last_name(),
                        "totalprice": random.randint(100, 1000),
                        "depositpaid": random.choice([True, False]),
                        "bookingdates": {"checkin": "2026-03-12",
                                         "checkout": "2026-03-15"},
                        "additionalneeds": "Lunch"}

        # Request POST to create new booking
        response = api_client.create_booking(booking_data=booking_data)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nCreateBooking response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body contains bookingid, store it -> received and stored
        assert "bookingid" in res_body
        assert api_client.booking_id is not None

        # Verify response body contains booking, store it -> received and stored
        assert "booking" in res_body
        assert api_client.booking_data is not None

        # Verify all booking details in response match creation data
        assert res_body["booking"] == api_client.booking_data


    def test_get_booking_by_id(self, api_client):
        logger.info(f"\nStep 3: When I retrieve the booking by ID"
                    f"\n\tThen all booking details match creation data")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBooking response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match creation data -> as expected
        assert res_body == api_client.booking_data


    def test_full_update_booking(self, api_client):
        logger.info(f"\nStep 4: When I fully update the booking (PUT with token)"
                    f"\n\tThen lastname and checkout are updated\n\tAnd all other fields are preserved")

        # Define updated booking data for request body
        api_client.booking_data["lastname"] = names.get_last_name()                                     # Updated
        api_client.booking_data["bookingdates"]["checkout"] = "2026-02-17"                              # Updated

        # Request PUT to update a current booking
        response = api_client.update_booking(booking_id=api_client.booking_id,
                                             booking_data=api_client.booking_data)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nUpdateBooking response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match updating data -> as expected
        assert res_body == api_client.booking_data


    def test_verify_full_update(self, api_client):
        logger.info(f"\nStep 5: When I retrieve the booking by ID"
                    f"\n\tThen the update is reflected correctly")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingById response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match updating data -> as expected
        assert res_body == api_client.booking_data

    @responses.activate
    def test_full_update_booking_with_expired_token_mocked(self, api_client):
        logger.info(f"\nStep 6: When I attempt to update the booking with an expired token (mocked)"
                    f"\n\tThen I receive 403 Forbidden")

        # Define response body of mocked PUT request
        response_body = {"error": "Token has expired", "status": "403 Forbidden"}

        # Mock PUT response with status 403 Forbidden
        responses.add(method=responses.PUT,
                      url=f"{os.getenv("MOCK_URL")}/booking/{api_client.booking_id}",
                      json=response_body,
                      adding_headers={"Content-Type": "application/json"},
                      status = 403)

        # Define updated booking data for request body
        update_data = {"firstname": api_client.booking_data["firstname"],                           # Preserved
                       "lastname": names.get_last_name(),                                           # Updated
                       "totalprice": api_client.booking_data["totalprice"],                         # Preserved
                       "depositpaid": api_client.booking_data["depositpaid"],                       # Preserved
                       "bookingdates": api_client.booking_data["bookingdates"],                     # Preserved
                       "additionalneeds": api_client.booking_data["additionalneeds"]}               # Preserved

        # Request PUT, 'responses' intercepts it, mocked response is returned
        response = api_client.update_booking_mocked(mocked_url=os.getenv("MOCK_URL"),
                                                    booking_id=api_client.booking_id,
                                                    booking_data=update_data)

        # Verify status code -> 403 Forbidden
        assert response.status_code == 403, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nUpdateBooking response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # # Verify response body -> {"error": "Token has expired", "status": "403 Forbidden"}
        assert res_body["error"] == response_body["error"]
        assert res_body["status"] == response_body["status"]


    def test_verify_full_update_booking_with_expired_token(self, api_client):
        logger.info(f"\nStep 7: When I retrieve the booking by ID"
                    f"\n\tThen all booking details remain unchange")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingById response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match updating data -> as expected
        assert res_body == api_client.booking_data


    def test_full_update_booking_without_cookie(self, api_client):
        logger.info(f"\nStep 8: When I attempt to update the booking without the Cookie header"
                    f"\n\tThen I receive 403 Forbidden")

        # Define updated booking data for request body
        update_data = {"firstname": api_client.booking_data["firstname"],                           # Preserved
                       "lastname": names.get_last_name(),                                           # Updated
                       "totalprice": api_client.booking_data["totalprice"],                         # Preserved
                       "depositpaid": api_client.booking_data["depositpaid"],                       # Preserved
                       "bookingdates": api_client.booking_data["bookingdates"],                     # Preserved
                       "additionalneeds": api_client.booking_data["additionalneeds"]}               # Preserved

        # Request PUT to update a current booking with missing Cookie header
        response = api_client.update_booking_without_cookie(booking_id=api_client.booking_id,
                                                            booking_data=update_data)

        # Verify status code -> 403 Forbidden
        assert response.status_code == 403, f"Request failed with status {response.status_code}"

        logger.info(f"\nGetBooking response: {response.text}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body -> 'Forbidden'
        assert response.text == "Forbidden"


    def test_verify_full_update_booking_without_cookie(self, api_client):
        logger.info(f"\nStep 9: When I retrieve the booking by ID"
                    f"\n\tThen all booking details remain unchange")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingById response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match updating data -> as expected
        assert res_body == api_client.booking_data


    def test_partial_update_booking(self, api_client):
        logger.info(f"\nStep 10: When I partially update the booking (PATCH with token)"
                    f"\n\tThen only firstname is updated\n\tAnd all other fields remain unchanged")

        # Define updated booking data for request body
        partial_data = {"firstname": names.get_first_name()}                                            # Updated

        # Request PATCH to partially update a current booking
        response = api_client.partial_update_booking(booking_id=api_client.booking_id,
                                                     booking_data=partial_data)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nPartialUpdateBooking response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match partially updating data -> as expected
        api_client.booking_data["firstname"] = partial_data["firstname"]
        assert res_body == api_client.booking_data


    def test_verify_partial_update_booking(self, api_client):
        logger.info(f"\nStep 11: When I retrieve the booking by ID"
                    f"\n\tThen the partial update is reflected correctly")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingById response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify all booking details in response match updating data -> as expected
        assert res_body == api_client.booking_data


    def test_delete_booking(self, api_client):
        logger.info(f"\nStep 12: When I delete the booking (DELETE with token)"
                    f"\n\tThen the deletion is successful")

        # Request DELETE to delete a booking
        response = api_client.delete_booking(booking_id=api_client.booking_id)

        # Verify status code -> 201 Created
        assert response.status_code == 201, f"Request failed with status {response.status_code}"

        logger.info(f"\nDeleteBooking response: {response.text}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body -> 'Created'
        assert response.text == "Created"


    def test_verify_delete_booking_by_getting_booking_by_id(self, api_client):
         logger.info(f"\nStep 13: When I attempt to retrieve the deleted booking"
                     f"\n\tThen I receive 404 Not Found")

         # Request GET to retrieve a specific booking based upon the booking id provided
         response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

         # Verify status code -> 404 Not Found
         assert response.status_code == 404, f"Request failed with status {response.status_code}"

         logger.info(f"\nGetBooking response: {response.text}")
         logger.info(f"\nResponse status code: {response.status_code}")

         # Verify response body -> 'Not Found'
         assert "Not Found" in response.text
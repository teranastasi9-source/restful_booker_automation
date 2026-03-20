import pytest, responses, random, os, names, logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

# Load environment variables (*.env)
load_dotenv()


@pytest.mark.workflow2
@pytest.mark.usefixtures("health_check")
class TestWorkFlow2:
    """ Workflow 2: Authentication Token Lifecycle """

    def test_create_token(self, api_client, api_validate):
        logger.info(f"Step 1: Given valid authentication credentials\n\tWhen I request an authentication token"
                    f"\n\tThen I receive a valid token\n")

        # Request POST to create token
        response = api_client.create_token(username=os.getenv("USER"),
                                           password=os.getenv("PASSWORD"))
        logger.info(f"CreateToken response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify token is in response body, then store it and check if len(token) >= 1
        api_validate.assert_token_received(response, api_client)


    def test_create_booking(self, api_client, api_validate):
        logger.info(f"Step 2: When I create a new booking (no auth required)"
                    f"\n\tThen the booking is created with unique ID\n")

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
        logger.info(f"CreateBooking response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify bookingid and booking are in response, then stored them
        api_validate.assert_booking_created(response, api_client)

        # Verify all booking details in response match creation data
        api_validate.assert_booking_data_matches(response, booking_data)


    def test_get_booking_by_id(self, api_client, api_validate):
        logger.info(f"Step 3: When I retrieve the booking by ID"
                    f"\n\tThen all booking details match creation data\n")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
        logger.info(f"GetBooking response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match creation data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_full_update_booking(self, api_client, api_validate):
        logger.info(f"Step 4: When I fully update the booking (PUT with token)"
                    f"\n\tThen lastname and checkout are updated\n\tAnd all other fields are preserved\n")

        # Define updated booking data for request body
        api_client.booking_data["lastname"] = names.get_last_name()                                     # Updated
        api_client.booking_data["bookingdates"]["checkout"] = "2026-02-17"                              # Updated

        # Request PUT to update a current booking
        response = api_client.update_booking(booking_id=api_client.booking_id,
                                             booking_data=api_client.booking_data)
        logger.info(f"UpdateBooking response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match updating data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_verify_full_update(self, api_client, api_validate):
        logger.info(f"Step 5: When I retrieve the booking by ID"
                    f"\n\tThen the update is reflected correctly\n")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
        logger.info(f"GetBookingById response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match updating data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)

    @responses.activate
    def test_full_update_booking_with_expired_token_mocked(self, api_client, api_validate):
        logger.info(f"Step 6: When I attempt to update the booking with an expired token (mocked)"
                    f"\n\tThen I receive 403 Forbidden\n")

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
        logger.info(f"UpdateBooking response: {response.json()}")

        # Verify status code -> 403 Forbidden
        api_validate.assert_status_code(response, 403)

        # Verify response body -> {"error": "Token has expired", "status": "403 Forbidden"}
        api_validate.assert_booking_data_matches(response, response_body)


    def test_verify_full_update_booking_with_expired_token(self, api_client, api_validate):
        logger.info(f"Step 7: When I retrieve the booking by ID"
                    f"\n\tThen all booking details remain unchange\n")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
        logger.info(f"GetBookingById response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match updating data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_full_update_booking_without_cookie(self, api_client, api_validate):
        logger.info(f"Step 8: When I attempt to update the booking without the Cookie header"
                    f"\n\tThen I receive 403 Forbidden\n")

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
        logger.info(f"GetBooking response: {response.text}")

        # Verify status code -> 403 Forbidden
        api_validate.assert_status_code(response, 403)

        # Verify response body -> 'Forbidden'
        api_validate.assert_test_response(response, "Forbidden")


    def test_verify_full_update_booking_without_cookie(self, api_client, api_validate):
        logger.info(f"Step 9: When I retrieve the booking by ID"
                    f"\n\tThen all booking details remain unchange\n")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
        logger.info(f"GetBookingById response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match updating data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_partial_update_booking(self, api_client, api_validate):
        logger.info(f"Step 10: When I partially update the booking (PATCH with token)"
                    f"\n\tThen only firstname is updated\n\tAnd all other fields remain unchanged\n")

        # Define updated booking data for request body
        partial_data = {"firstname": names.get_first_name()}                                            # Updated

        # Request PATCH to partially update a current booking
        response = api_client.partial_update_booking(booking_id=api_client.booking_id,
                                                     booking_data=partial_data)
        logger.info(f"PartialUpdateBooking response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match partially updating data -> as expected
        api_client.booking_data["firstname"] = partial_data["firstname"]
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_verify_partial_update_booking(self, api_client, api_validate):
        logger.info(f"Step 11: When I retrieve the booking by ID"
                    f"\n\tThen the partial update is reflected correctly\n")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
        logger.info(f"GetBookingById response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify all booking details in response match updating data -> as expected
        api_validate.assert_booking_data_matches(response, api_client.booking_data)


    def test_delete_booking(self, api_client, api_validate):
        logger.info(f"Step 12: When I delete the booking (DELETE with token)"
                    f"\n\tThen the deletion is successful\n")

        # Request DELETE to delete a booking
        response = api_client.delete_booking(booking_id=api_client.booking_id)
        logger.info(f"DeleteBooking response: {response.text}")

        # Verify status code -> 201 Created
        api_validate.assert_status_code(response, 201)

        # Verify response body -> 'Created'
        api_validate.assert_test_response(response, "Created")


    def test_verify_delete_booking_by_getting_booking_by_id(self, api_client, api_validate):
         logger.info(f"Step 13: When I attempt to retrieve the deleted booking"
                     f"\n\tThen I receive 404 Not Found\n")

         # Request GET to retrieve a specific booking based upon the booking id provided
         response = api_client.get_booking_by_id(booking_id=api_client.booking_id)
         logger.info(f"GetBooking response: {response.text}")

         # Verify status code -> 404 Not Found
         api_validate.assert_status_code(response, 404)

         # Verify response body -> 'Not Found'
         api_validate.assert_test_response(response, "Not Found")
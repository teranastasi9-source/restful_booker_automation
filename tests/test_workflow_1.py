import pytest, random, os, names, logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

# Load environment variables (*.env)
load_dotenv()


@pytest.mark.workflow1
@pytest.mark.usefixtures("health_check")
class TestWorkFlow1:
    """ Workflow 1: Full CRUD Lifecycle """

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
                        "bookingdates": {"checkin": "2026-02-12",
                                         "checkout": "2026-02-15"},
                        "additionalneeds": "Breakfast"}

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


    def test_get_all_booking_ids(self, api_client):
        logger.info(f"\nStep 3: When I retrieve all booking IDs"
                    f"\n\tThen the new booking appears in the list")

        # Request GET to retrieve ids of all the bookings that exist within the API
        response = api_client.get_all_booking_ids()

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingIds response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body contains booking_id of recently created booking -> booking_id is returned
        booking_ids = [booking["bookingid"] for booking in res_body]
        assert api_client.booking_id in booking_ids

        # Verify response contains exactly 1 occurrence of booking_id -> 1
        assert booking_ids.count(api_client.booking_id) == 1


    def test_get_booking_by_id(self, api_client):
        logger.info(f"\nStep 4: When I retrieve the booking by ID"
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
        logger.info(f"\nStep 5: When I fully update the booking (PUT with token)"
                    f"\n\tThen lastname and checkout are updated"
                    f"\n\tAnd all other fields are preserved")

        # Define updated booking data for request body
        api_client.booking_data["lastname"] = names.get_last_name()                                     # Updated
        api_client.booking_data["bookingdates"]["checkout"] = "2026-02-16"                              # Updated

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


    def test_verify_full_update_booking(self, api_client):
        logger.info(f"\nStep 6: When I retrieve the booking by ID"
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


    def test_partial_update_booking(self, api_client):
        logger.info(f"\nStep 7: When I partially update the booking (PATCH with token)"
                    f"\n\tThen only firstname is updated"
                    f"\n\tAnd all other fields remain unchanged")

        # Define updated booking data for request body
        partial_data = {"firstname": names.get_first_name()}                                        # Updated

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
        logger.info(f"\nStep 8: When I retrieve the booking by ID"
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
         logger.info(f"\nStep 9: When I delete the booking (DELETE with token)"
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
        logger.info(f"\nStep 10: When I attempt to retrieve the deleted booking"
                    f"\n\tThen I receive 404 Not Found")

        # Request GET to retrieve a specific booking based upon the booking id provided
        response = api_client.get_booking_by_id(booking_id=api_client.booking_id)

        # Verify status code -> 404 Not Found
        assert response.status_code == 404, f"Request failed with status {response.status_code}"

        logger.info(f"\nGetBooking response: {response.text}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body -> 'Not Found'
        assert "Not Found" in response.text


    def test_verify_delete_booking_by_getting_all_booking_ids(self, api_client):
        logger.info(f"\nStep 11: When I retrieve all booking IDs again"
                    f"\n\tThen the deleted booking no longer appears")

        # Request GET to retrieve ids of all the bookings that exist within the API
        response = api_client.get_all_booking_ids()

        # Verify status code -> 200 Success
        assert response.status_code == 200, f"Request failed with status {response.status_code}"

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"\nGetBookingIds response: {res_body}")
        logger.info(f"\nResponse status code: {response.status_code}")

        # Verify response body does NOT contain booking_id of recently deleted booking -> booking_id is NOT returned
        booking_ids = [booking["bookingid"] for booking in res_body]
        assert api_client.booking_id not in booking_ids

        # Verify response contains exactly 0 occurrence of booking_id -> 0
        assert booking_ids.count(api_client.booking_id) == 0
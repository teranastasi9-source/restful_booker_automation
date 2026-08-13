import logging
import os
import time

import pytest
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables (*.env)
load_dotenv()


@pytest.mark.workflow3
@pytest.mark.usefixtures("health_check")
class TestWorkFlow3:
    """ Workflow 3: Multiple concurrent bookings """

    # List to track all created booking IDs for uniqueness validation
    created_booking_ids = []

    def test_create_token(self, api_client, api_validate):
        """Verify a valid auth token is issued for correct credentials."""
        logger.info("Step 1: Given valid authentication credentials\n\tWhen I request an authentication token"
                    "\n\tThen I receive a valid token\n")

        # Request POST to create token
        response = api_client.create_token(username=os.getenv("USER"),
                                           password=os.getenv("PASSWORD"))
        logger.info(f"CreateToken response: {response.json()}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify token is in response body, then store it and check if len(token) >= 1
        api_validate.assert_token_received(response, api_client)


    @pytest.mark.parametrize("firstname, lastname, totalprice, depositpaid, checkin, checkout, additionalneeds",
                             [("John",    "Smith",   500, True,  "2026-03-01", "2026-03-07", "WiFi"),
                              ("Emma",    "Johnson", 300, False, "2026-03-07", "2026-03-10", "Breakfast"),
                              ("Michael", "Brown",   800, True,  "2026-03-12", "2026-03-18", "Lunch"),
                              ("Sarah",   "Davis",   450, True,  "2026-03-15", "2026-03-18", "Champagne"),
                              ("David",   "Wilson", 1200, False, "2026-03-08", "2026-03-16", "Extra Bed")],
                             ids=[i for i in range(1, 6)])
    def test_create_booking_various_travelers(self, api_client, api_validate, firstname, lastname, totalprice,
                                                                depositpaid, checkin, checkout, additionalneeds):
        """Verify each of several concurrently-created bookings gets a unique ID and stores its own data correctly."""
        logger.info("Step 2: When I create a new booking (no auth required)"
                    "\n\tThen the booking is created with unique ID\n\tAnd all booking details match creation data\n")

        # Define request body with booking details
        booking_data = {"firstname": firstname,
                        "lastname": lastname,
                        "totalprice": totalprice,
                        "depositpaid": depositpaid,
                        "bookingdates": {"checkin": checkin,
                                         "checkout": checkout},
                        "additionalneeds": additionalneeds}

        # Request POST to create new booking
        response = api_client.create_booking(booking_data=booking_data)

        # Convert response body to JSON format
        res_body = response.json()
        logger.info(f"CreateBooking response: {res_body}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify booking_id is unique (not created before in this test run)
        booking_id = res_body["bookingid"]
        assert booking_id not in self.created_booking_ids, f"Duplicate booking_id detected: {booking_id}"

        # Store booking_id for uniqueness validation in subsequent tests
        self.created_booking_ids.append(booking_id)

        # Verify all booking details in response match creation data
        assert res_body["booking"]["firstname"] == firstname
        assert res_body["booking"]["lastname"] == lastname
        assert res_body["booking"]["totalprice"] == totalprice
        assert res_body["booking"]["depositpaid"] == depositpaid
        assert res_body["booking"]["bookingdates"]["checkin"] == checkin
        assert res_body["booking"]["bookingdates"]["checkout"] == checkout
        assert res_body["booking"]["additionalneeds"] == additionalneeds


    def test_get_all_booking_ids(self, api_client, api_validate):
        """Verify all bookings created in the previous step appear in the full list, each exactly once."""
        logger.info("\nStep 3: When I retrieve all booking IDs"
                    "\n\tThen the new bookings appear in the list\n\tAnd each booking_id occurs once")

        # Request GET to retrieve ids of all the bookings that exist within the API
        response = api_client.get_all_booking_ids()
        res_body = response.json()
        logger.info(f"GetBookingIds response: {res_body}")
        logger.info(f"\nCreated booking IDs: {self.created_booking_ids}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify response body contains booking_id and occurs 1 time -> booking_id is returned
        booking_ids = [booking["bookingid"] for booking in res_body]
        for booking_id in self.created_booking_ids:
            assert booking_id in booking_ids, f"Created booking_id: {booking_id} isn`t present in all booking IDs list"
            assert booking_ids.count(booking_id) == 1, f"Created booking_id: {booking_id} occurs more than once"


    def test_get_all_booking_ids_filtered_by_name(self, api_client, api_validate):
        """Verify GetBookingIds' documented firstname/lastname query filters actually narrow
        the result set down to the matching booking(s)."""
        logger.info("Step 4: When I create a booking with a distinctive name and retrieve"
                    " booking IDs filtered by it\n\tThen only that booking is returned\n")

        # A common name like "John Smith" isn't unique on this shared public demo API - it has
        # accumulated hundreds of real "John"-named bookings from other people's test runs over
        # time (verified directly: filtering by firstname=John&lastname=Smith alone returned
        # 678 results, not 1). A timestamp-suffixed firstname sidesteps that collision, so this
        # test can actually trust its own result set instead of guessing.
        unique = int(time.time())
        firstname, lastname = f"FilterCheck{unique}", "Traveler"
        booking_data = {"firstname": firstname,
                        "lastname": lastname,
                        "totalprice": 111,
                        "depositpaid": True,
                        "bookingdates": {"checkin": "2026-04-01", "checkout": "2026-04-02"},
                        "additionalneeds": "None"}

        # Request POST to create a booking with the distinctive name
        create_response = api_client.create_booking(booking_data=booking_data)
        booking_id = create_response.json()["bookingid"]
        logger.info(f"CreateBooking response: {create_response.json()}")

        # Request GET with firstname/lastname filters, per the API's own docs (see
        # "API Documentation" in README)
        response = api_client.get_all_booking_ids(firstname=firstname, lastname=lastname)
        res_body = response.json()
        logger.info(f"GetBookingIds (filtered) response: {res_body}")

        # Verify status code -> 200 Success
        api_validate.assert_status_code(response, 200)

        # Verify the filtered result contains exactly the one booking just created, nothing else
        booking_ids = [booking["bookingid"] for booking in res_body]
        assert booking_ids == [booking_id], \
            f"Expected exactly [{booking_id}] for a uniquely-named booking.\nActual: {booking_ids}"

import requests, os, time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables (*.env)
load_dotenv()

class BookerAPIClient:
    """ RESTful Booker API with all possible HTTP methods """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.booking_id: Optional[int] = None
        self.booking_data: Optional[Dict[str, Any]] = None

    def _make_request(self, method: str, url: str,
                      max_time:str = os.getenv("MAX_RESPONSE_TIME"), **kwargs) -> requests.Response:
        """
        Internal helper to make requests and track response time
        All API methods use this internally.
        """
        start_time = time.time()
        response = self.session.request(method, url, **kwargs)
        end_time = time.time()
        response_time = round(((end_time - start_time) * 1000), 2)

        if response_time > int(max_time):
            raise TimeoutError(f"Response time {response_time}ms exceeds {max_time}ms")
        else:
            print(f"\nResponse time {response_time}ms is below {max_time}ms")
        return response

    def create_token(self, username: str, password: str) -> requests.Response:
        """ [POST] Create a new auth token to use for access to the PUT/PATCH and DELETE /booking """
        response = self._make_request(method="POST",
                                      url=f"{self.base_url}/auth",
                                      headers={"Content-Type": "application/json"},
                                      json={"username": username, "password": password})
        if response.status_code == 200:
            self.token = response.json().get("token")
        return response

    def create_booking(self, booking_data) -> requests.Response:
        """ [POST] Create a new booking in the API (no auth required) """
        response = self._make_request(method="POST",
                                      url=f"{self.base_url}/booking",
                                      json=booking_data,
                                      headers={"Content-Type": "application/json",
                                               "Accept": "application/json"})
        if response.status_code == 200:
            self.booking_id = response.json().get("bookingid")
            self.booking_data = response.json().get("booking")
        return response

    def get_booking_by_id(self, booking_id: int) -> requests.Response:
        """ [GET] Returns a specific booking based upon the booking id provided (no auth required) """
        return self._make_request(method="GET",
                                  url=f"{self.base_url}/booking/{booking_id}")

    def get_all_booking_ids(self) -> requests.Response:
        """ [GET] Returns the ids of all the bookings that exist within the API (no auth required) """
        return self._make_request(method="GET",
                                  url=f"{self.base_url}/booking",
                                  headers={"Content-Type": "application/json"})

    def update_booking(self, booking_id: int, booking_data: Dict[str, Any]) -> requests.Response:
        """ [PUT] Updates a current booking (auth required) """
        return self._make_request(method="PUT",
                                  url=f"{self.base_url}/booking/{booking_id}",
                                  json=booking_data,
                                  cookies={"token": self.token} if self.token else {},
                                  headers={"Content-Type": "application/json",
                                           "Accept": "application/json"})

    def partial_update_booking(self, booking_id: int, booking_data: Dict[str, Any]) -> requests.Response:
        """ [PATCH] Updates a current booking with a partial payload (auth required) """
        return self._make_request(method="PATCH",
                                  url=f"{self.base_url}/booking/{booking_id}",
                                  json=booking_data,
                                  cookies={"token": self.token} if self.token else {},
                                  headers={"Content-Type": "application/json",
                                           "Accept": "application/json"})

    def delete_booking(self, booking_id: int) -> requests.Response:
        """ [DELETE] Deletes a booking from the API (auth required) """
        return self._make_request(method="DELETE",
                                  url=f"{self.base_url}/booking/{booking_id}",
                                  cookies={"token": self.token} if self.token else {})

    def update_booking_mocked(self, mocked_url: str, booking_id: int,
                              booking_data: Dict[str, Any]) -> requests.Response:
        """ [PUT] Update booking with expired token (uses mock server) """
        return self._make_request(method="PUT",
                                  url=f"{mocked_url}/booking/{booking_id}",
                                  json=booking_data,
                                  cookies={"token": "ccb59d3efd94c3a"})

    def update_booking_without_cookie(self, booking_id: int, booking_data: Dict[str, Any]) -> requests.Response:
        """ [PUT] Update booking without Cookie header (auth required but missing) """
        return self._make_request(method="PUT",
                                  url=f"{self.base_url}/booking/{booking_id}",
                                  json=booking_data)
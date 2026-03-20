import pytest, requests, os
from api_tests.restful_booker_automation.libs.api_client import BookerAPIClient
from api_tests.restful_booker_automation.libs.api_validate import APIValidate
from dotenv import load_dotenv

# Load environment variables (*.env)
load_dotenv()

@pytest.fixture(scope="session")
def api_client():
    """ Session-scoped fixture: create API client once for all tests. Loads BASE_URL from .env file """
    yield BookerAPIClient(base_url=os.getenv("BASE_URL"))


@pytest.fixture(scope="class")
def health_check(api_client):
    """ Class-scoped fixture: simple health check endpoint to confirm whether the API is up and running
        Runs once at the beginning of TestWorkFlow1 and TestWorkFlow2 """
    try:
        response = requests.get(url=f"{api_client.base_url}/ping", timeout=5)
        assert response.status_code == 201, f"Healthcheck failed: {response.status_code}"
        print(f"\nHealthcheck passed: API is up and running at {api_client.base_url}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Healthcheck failed - API not available: {str(e)}")
    yield


@pytest.fixture(scope="function")
def api_validate():
    """ Function-scoped fixture: create instance for each test to perform validations"""
    max_time = int(os.getenv("MAX_RESPONSE_TIME", 1000))
    return APIValidate(max_response_time=max_time)
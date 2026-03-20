# RESTful Booker API Test Automation - Python + requests

Purpose: Python-based test automation framework for https://restful-booker.herokuapp.com. Portfolio demonstration of API automation and pytest best practices]

## Project Overview
|Aspect| Details                                    |
|------|--------------------------------------------|
|**API Under Test**| RESTful Booker (Public demo REST API)      |
|**Tool**| Pytest + requests + responses              |
|**Auth**| Token (Cookie)                             |
|**Test Types**| Integration Workflows + Mocked Response + Concurrency test |

## Comparison: Postman vs Python
|Aspect|Postman + Newman|Pytest + requests + responses|
|------|--------------|---------------------|
|**Setup**|Import collection|Install dependencies|
|**Execution**|`newman run`|`pytest`|
|**Mocking**|Postman Mock Server|`responses` library|
|**Reports**|HTML via htmlextra|HTML via pytest-html|
|**Maintainability**|GUI-based|Code-based|
> Note: Postman solution - https://github.com/teranastasi9-source/restful_booker_postman


## This project demonstrates:
  - REST API testing (CRUD operations, authentication, integration workflows, concurrency)
  - Pytest framework (fixtures, HTML report generation)
  - API Client Design (abstraction layer, session management, error handling)
  - Security Testing (token validation, expired tokens, missing authentication headers)
  - Mocking Strategy (isolation for impractical scenarios)
  - Documentation and reproducibility practices


##  Project structure
restful_booker_automation/
  - libs/
    - api_client.py           
    > API client wrapper for RESTful Booker
    - api_validate.py
    > validation methods for for RESTful Booker
  - reports/
    - report_IntegrationWorkflows.html
    > Generated HTML report
  - tests/
    - test_workflow_1.py     
    > Workflow 1: Full CRUD Lifecycle
    - test_workflow_2.py         
    > Workflow 2: Authentication Token Lifecycle
    - test_workflow_3.py    
    > Workflow 3: Multiple concurrent bookings
  - .env                         
    > Environment variables
  - pytest.ini                       
    > pytest configuration
  - requirements.txt
    > Python dependencies
  - README.md 


## Integration Workflows -> tests/
### Workflow 1: Full CRUD Lifecycle -> test_workflow_1.py
    [Given valid authentication credentials
    When I request an authentication token
    Then I receive a valid token

    When I create a new booking (no auth required)
    Then the booking is created with unique ID

    When I retrieve all booking IDs
    Then the new booking appears in the list

    When I retrieve the booking by ID
    Then all booking details match creation data

    When I fully update the booking (PUT with token)
    Then lastname and checkout are updated
    And all other fields are preserved

    When I retrieve the booking by ID
    Then the update is reflected correctly

    When I partially update the booking (PATCH with token)
    Then only firstname is updated
    And all other fields remain unchanged

    When I retrieve the booking by ID
    Then the partial update is reflected correctly
    
    When I delete the booking (DELETE with token)
    Then the deletion is successful
    
    When I attempt to retrieve the deleted booking
    Then I receive 404 Not Found

    When I retrieve all booking IDs again
    Then the deleted booking no longer appears]

### Workflow 2: Authentication Token Lifecycle -> test_workflow_2.py
    [Given valid authentication credentials
    When I request an authentication token
    Then I receive a valid token

    When I create a new booking (no auth required)
    Then the booking is created with unique ID

    When I retrieve the booking by ID
    Then all booking details match creation data

    When I fully update the booking (PUT with token)
    Then lastname and checkout are updated
    And all other fields are preserved

    When I retrieve the booking by ID
    Then the update is reflected correctly

    When I attempt to update the booking with an expired token (mocked)
    Then I receive 403 Forbidden

    When I retrieve the booking by ID
    Then all booking details remain unchanged
    
    When I attempt to update the booking without the Cookie header
    Then I receive 403 Forbidden

    When I retrieve the booking by ID
    Then all booking details remain unchange

    When I partially update the booking (PATCH with token)
    Then only firstname is updated
    And all other fields remain unchanged

    When I retrieve the booking by ID
    Then the partial update is reflected correctly

    When I delete the booking (DELETE with token)
    Then the deletion is successful

    When I attempt to retrieve the deleted booking
    Then I receive 404 Not Found]

### Workflow 3: Multiple concurrent bookings -> test_workflow_3.py
    [Given valid authentication credentials
    When I request an authentication token
    Then I receive a valid token

    When I create a new booking (no auth required)
    Then the booking is created with unique ID
    And all booking details match creation data

    When I create a new booking (no auth required)
    Then the booking is created with unique ID
    And all booking details match creation data

    When I create a new booking (no auth required)
    Then the booking is created with unique ID
    And all booking details match creation data

    When I create a new booking (no auth required)
    Then the booking is created with unique ID
    And all booking details match creation data

    When I create a new booking (no auth required)
    Then the booking is created with unique ID
    And all booking details match creation data

    When I retrieve all booking IDs
    Then the new bookings appear in the list
    And each booking_id occurs once]


## Prerequisites
- Python 3.8+ installed


## Test execution
### Rename .env.example file to .env

### Clone the repository
git clone https://github.com/yourusername/restful_booker_automation.git

### Install dependencies
pip install -r requirements.txt

### Run specific test
pytest tests/test_workflow_1.py -v -s
pytest -m workflow3

### Run all tests
pytest tests/ -v -s


## Expected output
After running, you should see:
  - All tests executed successfully
  - HTML report generated in reports/report_IntegrationWorkflows.html
  - test log generated in reports/test_logs.log

Report includes:
  - Pass/fail status per test step
  - Test step duration
  - Summary dashboard


## Troubleshooting
Issue: ModuleNotFoundError: No module named '...'
  → Run: pip install -r requirements.txt


## Contact
- Anastasiia Zatorska
- Email: teranastasi9@gmail.com
- LinkedIn: http://www.linkedin.com/in/anastasiia9-zatorska
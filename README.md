# RESTful Booker API Test Automation - Python + requests

[![Tests](https://github.com/teranastasi9-source/restful_booker_automation/actions/workflows/tests.yml/badge.svg)](https://github.com/teranastasi9-source/restful_booker_automation/actions/workflows/tests.yml)

Purpose: Python-based test automation framework for https://restful-booker.herokuapp.com. Portfolio demonstration of API automation and pytest best practices.

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


## Project structure
```
restful_booker_automation/
  .github/workflows/tests.yml          - CI: lint + tests on push/PR, nightly schedule, manual
  .claude/skills/                        - project-scoped Claude Code skills (see below)
  CLAUDE.md                                - code-review checklist read by Claude Code
  docs/report_screenshot.png                 - report screenshot embedded below, for a no-clone preview
  pyproject.toml                               - ruff config
  requirements-dev.txt                           - + ruff, for linting
  libs/
    api_client.py                                    - API client wrapper for RESTful Booker
    api_validate.py                                  - validation methods for RESTful Booker
  reports/
    report_IntegrationWorkflows.html                   - generated HTML report
    test_logs.log                                      - generated text log
  tests/
    conftest.py                                          - fixtures (api_client, health_check, api_validate)
    test_workflow_1.py                                     - Workflow 1: Full CRUD Lifecycle
    test_workflow_2.py                                     - Workflow 2: Authentication Token Lifecycle
    test_workflow_3.py                                     - Workflow 3: Multiple concurrent bookings
  .env                                              - environment variables (not committed)
  pytest.ini                                          - pytest configuration
  requirements.txt                                      - Python dependencies
```


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
### Rename 'env.example' file to '.env'

### Clone the repository
git clone https://github.com/teranastasi9-source/restful_booker_automation.git

### Install dependencies
pip install -r requirements.txt

### Run specific test
- pytest tests/test_workflow_1.py -v -s
- pytest -m workflow3

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

A recent run's report is committed at `reports/report_IntegrationWorkflows.html` so you can
see the results without running anything - open it directly in a browser.

![HTML test report](docs/report_screenshot.png)


## Linting

Code style is checked with [ruff](https://docs.astral.sh/ruff/) (config in `pyproject.toml`).

```bash
pip install -r requirements-dev.txt
ruff check .          # report issues
ruff check . --fix    # auto-fix what can be auto-fixed (import sorting, unused imports, ...)
```

## CI

Runs on every push/PR, plus a daily scheduled run and manual `workflow_dispatch` (see
`.github/workflows/tests.yml`). If the **scheduled** run fails, a GitHub Issue is opened
automatically (push/PR/manual runs are already being watched live, so they don't) - a "don't
let this go unnoticed" safety net, not a verdict on whether it's a real regression or an
external-API hiccup (see the `triage-api-test-failure` skill).


## Troubleshooting
Issue: ModuleNotFoundError: No module named '...'
  → Run: pip install -r requirements.txt


## Working with Claude Code

This project is read by [Claude Code](https://claude.com/claude-code) via `CLAUDE.md`
(a standing code-review checklist) and three custom project-scoped skills in
`.claude/skills/`:

- **`add-workflow-step`** - the recipe for extending a workflow class or adding a new one:
  where API client methods / validation helpers go, the docstring + Given/When/Then logging
  convention, and - the most important step - verifying real API behavior before writing an
  assertion about it, instead of guessing.
- **`triage-api-test-failure`** - a decision process for telling a real regression apart from
  an external API hiccup (this API runs on a free Heroku dyno, same cold-start pattern as the
  `playwright_ui_automation` sibling project) or a state/ordering bug specific to this repo's
  intentionally stateful workflow-class design.
- **`create-bug-ticket`** - once a failure is triaged and confirmed real, files it as a GitHub
  Issue: drafts the title/repro steps/expected-vs-actual for review first, then files via
  `gh issue create` - never auto-filed, and never for a failure that turned out to be the known
  Heroku cold-start flake or a state/ordering issue between two steps. CI also opens an issue
  automatically for a failed scheduled nightly run (see "CI" below) - this skill covers the
  other case, when you notice a failure yourself.

All three mirror the equivalent skills in `playwright_ui_automation`, adapted to this repo's
own conventions rather than copied as-is - the two projects share a review philosophy, not
identical rules.


## Contact
- Anastasiia Zatorska
- Email: teranastasi9@gmail.com
- LinkedIn: http://www.linkedin.com/in/anastasiia9-zatorska

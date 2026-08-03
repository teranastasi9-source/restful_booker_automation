---
name: add-workflow-step
description: Add a new test step to one of this project's API workflow classes, or a new workflow file, following its established conventions (docstrings, Given/When/Then logging, verified assertions, ordered/stateful steps). Use when asked to add, write, or extend a workflow test in restful_booker_automation.
---

# Add a workflow step

This project tests the RESTful Booker API as ordered, stateful workflows (see `CLAUDE.md` for
the full review checklist) — not independent, isolated test cases. Follow this recipe instead
of writing something ad hoc.

## 1. Decide where it goes

- **A new step in an existing user journey** (e.g. one more assertion after delete): add a new
  test method at the end of the relevant `TestWorkFlow*` class, in `tests/test_workflow_N.py`.
  It runs after every existing method in that class and can rely on `api_client`'s current
  state (`token`, `booking_id`, `booking_data`) exactly as the method before it left it.
- **A genuinely new, independently-meaningful journey**: add a new `tests/test_workflow_N.py`
  file with its own `TestWorkFlowN` class, its own `@pytest.mark.workflowN` marker (register it
  in `pytest.ini`'s `markers` list), and `@pytest.mark.usefixtures("health_check")` at the
  class level, matching the existing three.
- **A new API operation** (e.g. a new endpoint): add a method to `BookerAPIClient` in
  `libs/api_client.py`, routed through `_make_request` like every other method there — don't
  call `requests` directly from a test.
- **A new kind of assertion** used more than once: add a method to `APIValidate` in
  `libs/api_validate.py` rather than repeating raw `assert` logic across test files.

## 2. Verify before you assert — this is the most important step

Before writing any assertion about what the API is supposed to return for a new
endpoint/scenario, check it for real first:

- Hit the real endpoint with the actual client (or a throwaway `requests` script) and look at
  the actual status code and response body — don't guess from the RESTful Booker docs alone,
  since demo APIs can drift from their own documentation.
- Remember `restful-booker.herokuapp.com` is a **shared public demo** — other people's
  bookings already exist in it. Never assert on a total count or a fixed list; only assert
  that the ID/data *your test just created* behaves as expected.

## 3. Write the test

- Method name: describe what it verifies (`test_verify_delete_booking_by_getting_booking_by_id`),
  not just the step number — the docstring carries the step framing, the name carries intent.
- One-line docstring, `"""Verify ..."""` phrasing.
- `logger.info(...)` at the top narrating it Given/When/Then, with a `Step N:` prefix matching
  this file's existing numbering.
- Use `names`/`random` for any field that doesn't need to be deterministic, to avoid collisions
  with data from other runs or other users of the shared public API.
- If the scenario is something the real API can't produce on demand (an expired token, a
  specific error condition), mock it with `responses` (`@responses.activate`) instead of trying
  to force the real API into that state — see `test_full_update_booking_with_expired_token_mocked`.
- Don't add a separate response-time assertion — `_make_request` already enforces
  `MAX_RESPONSE_TIME` on every call made through `api_client`.

## 4. Verify it actually works

1. Run just the new/changed file: `pytest tests/test_workflow_N.py -v -s`.
2. Run the full suite once: `pytest tests/ -v -s` — confirm no regressions, and that step
   ordering within the class still holds (a state-dependent step failing right after a passing
   one usually means an ordering or state-mutation bug, not a flaky external failure — see the
   `triage-api-test-failure` skill to tell the two apart).

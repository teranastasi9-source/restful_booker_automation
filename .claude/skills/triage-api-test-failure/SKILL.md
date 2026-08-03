---
name: triage-api-test-failure
description: Diagnose whether a failing test in this project is a real bug/regression or an external-dependency issue (the free Heroku-hosted demo API being slow, down, or its shared public data behaving unexpectedly) — or a state/ordering bug from this repo's stateful workflow-class design. Use when a test fails and it's unclear whether the code or the API is at fault.
---

# Triage an API test failure

This project hits a real, free, publicly-shared demo API
(`restful-booker.herokuapp.com`) for almost everything. A failure can mean a real regression,
an external hiccup, or — specific to this repo's design — a step running out of order or a
previous step's state not being what a later step expects. Work through this before changing
any code.

## 1. Re-run it in isolation

```bash
pytest tests/test_workflow_N.py::TestWorkFlowN::test_name -v -s
```

- **Passes alone but fails as part of the full class?** That's a strong signal of a
  state/ordering problem, not an external issue — see step 4.
- **Still fails the same way, alone?** Continue to step 2.

## 2. Read the actual error, don't skim it

- A connection error, or a `TimeoutError` raised by `_make_request` itself (see
  `libs/api_client.py`) almost always points at the external API, not this codebase — the
  free Heroku dyno this API runs on can be slow to respond after being idle, the same pattern
  as `the-internet.herokuapp.com` in the `playwright_ui_automation` sibling project.
- A status-code or body mismatch (`assert_status_code`/`assert_booking_data_matches` failure)
  is more likely a real bug or a real regression — but confirm with step 3 before concluding.
- A `KeyError`/`AttributeError` on the response body usually means the API's real response
  shape doesn't match what the code assumes — verify the actual current shape (step 3) rather
  than patching around it blind.

## 3. Verify the external state directly, independent of pytest

Don't debug through the full pytest+fixture stack first. Hit the same endpoint directly (a
throwaway `requests` call, or `curl`) and look at what actually comes back right now:

- Is the API reachable at all? (`GET /ping` should return 201 — this repo's own
  `health_check` fixture already does exactly this at the start of every workflow class.)
- Does the real response actually match what the failing assertion expected?
- If the failure involves `test_get_all_booking_ids` or anything that lists bookings,
  remember this is a **shared public API** — other people's data is in there too. A failure
  here almost always means the test wrongly assumed something about the *total* list (count,
  full contents) instead of only checking its own created/deleted ID's presence — that's a
  code bug in the test, not the API's fault.

## 4. State/ordering bugs specific to this repo's design

Unlike a suite built for full test isolation, these workflow classes are *intentionally*
stateful: `api_client.token`, `api_client.booking_id`, `api_client.booking_data`, and
class-level lists like `created_booking_ids` are set by one test method and read by a later
one, in file order. If a test fails only when run after a specific other test (or only in a
certain run order):

- Check whether an earlier step actually completed and set the state this step depends on
  (e.g. did `test_create_booking` actually run and set `api_client.booking_id` before this one
  reads it?).
- Check whether two tests are mutating the *same* shared state in a way that conflicts —
  this is a real risk if a new test is inserted in the middle of an existing sequence instead
  of appended at the end.
- This is a genuine code bug to fix (a real dependency was broken or introduced out of order),
  not something a rerun or "flaky" marker should paper over.

## 5. Decide, then act — don't paper over a real bug

- **Confirmed external/environmental** (Heroku cold start, transient network blip): consider
  whether the call needs more headroom, but don't just retry until green without understanding
  why — the response-time budget in `.env` (`MAX_RESPONSE_TIME`) already exists specifically to
  catch a genuinely slow response, so don't casually inflate it to make a real slowdown disappear.
- **Confirmed state/ordering bug**: fix the actual dependency issue, don't reorder tests by
  trial and error — trace exactly which state the failing step needs and where it should have
  come from.
- **Confirmed real bug**: fix the actual cause. Never loosen an assertion to match whatever the
  code currently returns without first verifying (step 3's method) that the new expected value
  is actually correct.
- Either way, re-run the full suite (`pytest tests/ -v -s`) afterward to confirm the fix didn't
  break a later, dependent step.

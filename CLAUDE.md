# Instructions for Claude Code — restful_booker_automation

This file is read automatically by [Claude Code](https://claude.com/claude-code) at the
start of every session in this repo. It encodes the quality bar I (the repo owner, an
Automation QA engineer) hold AI-assisted changes to here — the point is to keep review
consistent regardless of who/what wrote the code, not to hand off judgment to the AI.

This project is the API-testing counterpart to my `playwright_ui_automation` repo (UI). Some
conventions are deliberately shared (docstrings, Given/When/Then logging); others are
deliberately different, because this repo tests stateful multi-step API workflows instead of
independent UI scenarios — see "Test data & state" below before assuming a UI-testing rule
applies here unchanged.

## Code review process

Whenever asked to review code in this project, always:

1. **Run ruff first**: `cd restful_booker_automation && ruff check .` (add `--fix` only if
   asked to auto-fix, otherwise just report findings). Report every finding, don't silently
   skip any.
2. **Check the code against the API test best-practices checklist below.** Flag violations as
   review findings, don't just fix them silently — explain what's wrong and why.
3. **Scan for stale comments or leftover files that don't match current test code.** This repo
   has real history of this: an old draft of `test_workflow_3.py` was left behind at the repo
   root as a stray untracked file (`_orig_check`) after a rewrite, never cleaned up. Don't
   assume every file in the repo root is meant to be there.
4. **Don't trust a comment about live API behavior without verifying it.** If adding a new
   endpoint/assertion, hit the real API (or check `reports/report_IntegrationWorkflows.html`
   from a recent run) before writing an assertion about what it returns — the same rule as
   the UI sibling project, for the same reason (comments about external behavior rot quietly).
5. **Watch for duplicated hardcoded values** that should route through `.env` (via
   `os.getenv(...)`) or a single shared constant instead of being repeated inline across test
   files (e.g. the valid username/password, or a threshold value).
6. **Never let a real secret reach `.env` without `.gitignore` covering it.** The credentials
   currently in `.env` are the public, documented restful-booker demo credentials
   (`admin`/`password123`) — not sensitive — but if this pattern is ever reused for a project
   with real credentials, confirm `.gitignore` excludes `.env` *before* anything is staged.

## API test best-practices checklist

### Test data & state
- The three workflow classes (`TestWorkFlow1/2/3`) are **intentionally stateful and
  order-dependent** — each test method mutates shared state (`api_client.token`,
  `api_client.booking_id`, `api_client.booking_data`, or a class-level list like
  `created_booking_ids`) and later steps rely on earlier ones having already run, in file
  order, within the same class. This mirrors a real multi-step user journey on purpose. Don't
  try to make these tests independent, and never reorder or randomly parametrize them in a
  way that could execute them out of sequence — that's a different philosophy from the UI
  sibling project's per-test isolation, not an oversight here.
- `restful-booker.herokuapp.com` is a **shared public demo API** — other people's bookings
  coexist in the same list. Never assert on the total booking count or an exact full list;
  only assert that *your own* created `booking_id` appears (or, after deletion, no longer
  appears) in it — see `test_get_all_booking_ids` for the right pattern.
- Randomize non-critical fields (`names`, `random.randint`, etc.) so concurrently-run test
  data can't collide with another run's, but always assert against the data you actually sent
  — never hardcode an expected response body that varies per run.

### API client design
- All HTTP calls go through `BookerAPIClient` (`libs/api_client.py`) via its internal
  `_make_request`, not raw `requests` calls inline in a test — that's what keeps the
  response-time check and any future shared header/auth change in one place.
- Auth token and current booking state live on the session-scoped `api_client` fixture
  instance. Don't introduce a second, parallel way of tracking either.
- `_make_request`'s `max_time` parameter used to default from `os.getenv("MAX_RESPONSE_TIME")`
  evaluated at *function-definition* time instead of per-call — a real bug, fixed 2026-08-14
  (the env var is now read inside the function body; the default argument itself is a plain
  `None`). Flag it if you see the same default-arg-reads-env-var shape introduced anywhere
  else in new code.

### Mocking
- Use `responses` (`@responses.activate`) only for scenarios the real API can't produce on
  demand — e.g. an expired token (see `test_full_update_booking_with_expired_token_mocked`).
  Don't mock something the real API can already validate for you; that just adds a second
  source of truth to keep in sync with reality.

### Response-time assertions
- `_make_request` already raises `TimeoutError` itself whenever a response exceeds
  `MAX_RESPONSE_TIME` (from `.env`) — every request made through the client gets this for
  free. Don't add a second, separate timing assertion inside a test body.

### Reporting
- Every test needs a one-line `"""Verify ..."""` docstring and a `logger.info(...)`
  Given/When/Then narration at the top, matching the existing tests — same convention as
  `playwright_ui_automation`, so the two repos read as one person's work.

## Running the suite

See `README.md` for setup (copy `env.example` to `.env`), run commands
(`pytest -m workflow3`, etc.), and the linting command.

---
name: create-bug-ticket
description: File a GitHub Issue for a test failure in this project that has been triaged and confirmed as a real bug (not an external-API flake or a state/ordering issue). Use after a test fails and the cause is understood, when it's worth tracking as a ticket.
---

# Create a bug ticket

GitHub Issues on this same repo is the ticket tracker here - free, and already where the code
and CI live, so no separate tool/account is needed. This project's CI also opens an issue
automatically when the **scheduled nightly run** fails (see `.github/workflows/tests.yml`) -
this skill is for the other case: you noticed a failure yourself (locally, or on a push/PR
run) and want it filed properly.

## 1. Triage first - a ticket is not the default outcome of a red test

Run the `triage-api-test-failure` skill's process before this one. Only continue here if it
concludes "confirmed real bug":

- A known external hiccup (the free Heroku dyno being slow to wake up) does **not** get a
  ticket on its own - re-run to confirm it's not transient first.
- A **state/ordering bug** (a workflow class's steps failing because an earlier step's state
  wasn't what a later step expected) is a real bug, but describe it as that specifically, not
  as a generic "test X failed" - the fix is almost always about the dependency between two
  specific steps, not the assertion itself.
- If triage is inconclusive, that's a reason to keep investigating, not to file a vague ticket
  now and figure it out later.

## 2. Draft the issue - never file blind

Compose, then show the full draft in chat before doing anything else:

- **Title**: `<test_file>::<ClassName>::<test_name> - <one-line symptom>`, e.g.
  `test_workflow_2.py::TestWorkFlow2::test_verify_full_update_booking_with_expired_token - stale booking data returned`
- **Body**, in this order:
  1. **What failed** - the test's own one-line "Verify ..." docstring.
  2. **Reproduce** - the exact command. Because these workflow classes are intentionally
     stateful and order-dependent (see `CLAUDE.md`), a single `::test_name` in isolation often
     won't reproduce it - use `pytest tests/test_workflow_N.py -v --tb=long` to run the whole
     class from the start, unless the failure is confirmed independent of earlier steps.
  3. **Expected vs. actual** - the real values from the assertion failure, not a paraphrase.
  4. **Environment** - Python/pytest/requests versions (from `reports/report_IntegrationWorkflows.html`'s
     Environment table).
  5. **Evidence** - the relevant traceback lines. If it's a suspected state/ordering bug, also
     note which earlier step's state the failing assertion depended on.

## 3. File it - only after I've confirmed the draft

- Check first that this isn't already filed: `gh issue list --search "<test_name>" --state open`
- File with: `gh issue create --title "<title>" --body "<body>" --label bug`
  (if the `bug` label doesn't exist yet: `gh label create bug --color d73a4a`)
- If `gh` isn't installed or authenticated on this machine, don't install/authenticate it
  unattended - instead build a prefilled "new issue" URL and hand it to me to open and submit
  myself:
  `https://github.com/<owner>/<repo>/issues/new?title=<url-encoded-title>&body=<url-encoded-body>`

## 4. Never

- File without independently reproducing the failure first - step 1's triage *is* that
  reproduction step, don't skip straight here from a single red run.
- File without showing the draft in chat first - filing a public issue is a visible, external
  action; I want to see the exact title/wording before it's posted, every time.
- File a duplicate of an already-open issue for the same test/cause, or of an issue CI already
  opened automatically for the same nightly failure.
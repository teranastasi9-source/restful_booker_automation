---
name: write-commit-message
description: House style for git commit messages in this repo - use whenever creating a commit here, whether Claude or the repo owner is the one typing it. Calibrates message depth to the actual size of the change instead of a uniform, verbose template.
---

# Write a commit message

This is a portfolio repo a technical interviewer may actually read commit-by-commit. A commit
history where every single message is a uniformly long, formally-structured explanation reads
as automated, not as one engineer's judgment calls - regardless of whether that's literally
true. The fix isn't hiding that Claude Code is used (`CLAUDE.md` already says so openly) - it's
writing messages the way a person actually would: effort matched to the change, not a template
applied uniformly regardless of size.

## 1. Match depth to the actual change - most commits should be short

- **Trivial** (typo, one-line config value, wording fix, dependency bump): subject line only,
  no body. The diff already shows what changed - don't narrate it.
- **Small/routine** (a new test, a straightforward refactor, a doc section): subject line + at
  most one short sentence of body, only if the *why* genuinely isn't obvious from the subject
  and diff alone.
- **Genuinely non-obvious** (a real bug fix, a design tradeoff, something a reviewer would
  otherwise ask "wait, why?" about): a fuller body is warranted - but write it like a note to a
  colleague, not an incident report (see the before/after below).

Look back at the last 5 commits before writing a new one. If they're all roughly the same
length and shape, that's the smell this skill exists to fix - vary it.

## 2. Subject line

Imperative mood, no trailing period, ideally under ~65 characters. `Fix X` / `Add Y` / `Remove
Z`, not `Fixed`, `Added`, `This commit adds`.

## 3. Avoid these patterns even when the body is warranted

- Don't cite how/when something was verified inside the message itself (`Verified 2026-08-05
  via...`, `Reproduced by...`). Do the verification; don't write it up like a lab report. If it
  genuinely needs to be on record, that's what a PR description or an issue comment is for, not
  every commit.
- Don't use a recurring rigid template (`Problem: ... / Solution: ... / Verified: ...`) across
  commits - even a good template becomes a tell once it's identical every time.
- Don't restate the diff in prose (`Added X. Changed Y. Removed Z.`) - say why, not what.
- Don't hedge with filler transitions - `Note that...`, `It's worth mentioning...`, `This
  ensures that...`. State the reason plainly.
- Never add a `Co-Authored-By` trailer for Claude in this repo's commits.

## 4. Before / after

**Trivial change** - a static badge added to the README:

> Bad: *"Add static test-count badge to README\n\nAdded a static shields.io badge showing the
> current test count (31 tests) to the README, since a real coverage tool isn't set up here.
> This gives visitors a quick, no-clone signal of the suite's size. Note that this is a manual
> snapshot and will need to be updated by hand if the test count changes significantly."*
>
> Good: `Add static test-count badge to README (31 tests)` - subject only. The diff is one
> badge line.

**Genuinely non-obvious fix** - the artifact-collision bug this repo actually hit (kept short,
not restructured into a report):

> Bad: *"Delete stale github-pages artifact before uploading, to survive re-runs\n\nMirrors the
> fix in the playwright_ui_automation sibling project: re-running this workflow leaves a
> previous attempt's already-uploaded github-pages artifact in place, causing deploy-pages to
> fail with 'Multiple artifacts named github-pages... Artifact count is 2' on the second
> attempt. Deletes any leftover one via the API first (requires actions: write); no-op on a
> normal first attempt."*
>
> Good: *"Delete stale github-pages artifact before uploading, to survive re-runs\n\nRe-running
> a workflow whose pages job already succeeded leaves a duplicate github-pages artifact behind,
> which breaks deploy-pages on the second attempt. Clean it up first (same fix as the
> playwright_ui_automation sibling project)."*

Same information, a fraction of the length, reads like a person who understood the bug and
moved on - not a report justifying the change to a skeptical reader.

## 5. When Claude is asked to commit

Apply this skill by default, without being asked each time. If a commit is trivial, propose (or
just make) a subject-only message rather than defaulting to a body "to be thorough."
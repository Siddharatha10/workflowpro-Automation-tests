# Test Execution Report

**Run against:** bundled mock server (`mock_server/app.py`), `TEST_ENV=local`
**Date:** 2026-07-14

## Summary

| Layer | Tests | Result |
|---|---|---|
| API — tenant isolation (`test_tenant_isolation`) | 1 | ✅ PASSED (real run — see `junit.xml`, `report.html`) |
| UI — login, multi-tenant, project flow, mobile emulation | 5 | ⚠️ Not executed here — see limitation below |

## What was actually verified in this environment
This sandbox has network access to package registries only, so Playwright's browser
binaries (Chromium/Firefox/WebKit) couldn't be downloaded — `python -m playwright install`
fails silently with no route to the download CDN. Everything that only needs an HTTP
client, however, was run for real against the mock server:

- `test_tenant_isolation` — pytest run, **passed**, artifacts in `junit.xml` / `report.html`.
- Manual curl verification (see below) of the three behaviors the case study calls out:
  - `admin@company1.com` logs in with no 2FA step.
  - A project created by company1 is visible to a company1 token.
  - A company2 token requesting that same project ID gets **HTTP 404** (isolation holds,
    and the API doesn't leak that the resource exists via a 403 instead).

```
POST /api/v1/auth/login {company1}        -> 200, token issued
POST /api/v1/projects   {as company1}     -> 201, project id=3 created
GET  /api/v1/projects/3 {as company2}     -> 404  (tenant isolation confirmed)
```

## What is written and ready but not executed here
`tests/test_login.py` and the UI/mobile parts of
`tests/integration/test_project_creation_flow.py` depend on the `page`/`browser`
Playwright fixtures. They are complete, use the Page Object Model in `pages/`, and will
run as-is once browsers are installed:

```bash
python -m playwright install chromium
pytest tests/ -v
```

This is the same category of honest limitation as the BrowserStack step in Part 3 of the
design doc — the code path is real, the specific network dependency isn't reachable from
this sandbox.

## Raw artifacts
- `reports/junit.xml` — machine-readable result of the run that did execute.
- `reports/report.html` — self-contained HTML report (open directly in a browser).

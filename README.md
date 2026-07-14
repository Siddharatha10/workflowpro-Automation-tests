# workflowpro-tests

QA automation suite for "WorkFlow Pro" — a B2B multi-tenant project-management SaaS.
Covers login/2FA, tenant isolation, and the project-creation flow across web UI,
REST API, and mobile.

See [`TEST_PLAN.md`](TEST_PLAN.md) for scope/risk/strategy and
[`reports/TEST_EXECUTION_REPORT.md`](reports/TEST_EXECUTION_REPORT.md) for the last real
run's results.

## Structure

```
workflowpro-tests/
├── pages/              # Page Object Model (UI layer)
├── api/                # thin REST client classes
├── tests/
│   ├── test_login.py
│   └── integration/test_project_creation_flow.py
├── utils/data_factory.py
├── mock_server/        # local Flask stand-in for WorkFlow Pro (async load, 2FA, isolation)
├── test_data/           # seed accounts used against the mock server
├── conftest.py          # shared fixtures: api_token, test_project (self-cleaning)
├── config.py             # env-driven base URLs / tenants / credentials
├── pytest.ini
└── requirements.txt
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium   # needed for the UI/mobile tests
```

## Running against the bundled mock server (no external dependencies)

```bash
python mock_server/app.py &            # starts on http://localhost:5055
export TEST_ENV=local
pytest tests/ -v
```

## Running against a real environment

```bash
export TEST_ENV=staging
export WFP_COMPANY1_ADMIN_EMAIL=... WFP_COMPANY1_ADMIN_PASSWORD=...
export WFP_COMPANY2_USER_EMAIL=...   WFP_COMPANY2_USER_PASSWORD=...
export WFP_TEST_OTP=...
pytest tests/ -v -m smoke              # or -m regression for the full suite
```

Never commit real credentials — `config.py` only reads them from the environment
(CI secrets in a pipeline).

## Mobile / BrowserStack

`test_mobile_accessibility_emulated` uses a Playwright-emulated iPhone context locally.
For real-device coverage in CI, swap the `browser.new_context(**mobile)` call for
`playwright.chromium.connect(browserstack_cdp_url)` — same assertions, real hardware.

## Reports

`pytest.ini` wires up `pytest-html` and JUnit XML automatically; after any run, open
`reports/report.html` or feed `reports/junit.xml` to your CI's test reporter.

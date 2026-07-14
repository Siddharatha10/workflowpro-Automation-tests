# Test Plan — WorkFlow Pro (B2B SaaS)

## 1. Scope
Automated coverage for login/authentication, multi-tenant data isolation, and the
project-creation flow across web UI, backend API, and mobile viewport.

| In scope | Out of scope (flagged, not assumed) |
|---|---|
| Login incl. 2FA branch | Native mobile apps (Appium) — assumed responsive web only, see §5 |
| Tenant isolation (UI + API) | Payment/billing flows |
| Project creation (API → UI → mobile) | Full RBAC matrix (Admin/Manager/Employee) — only Admin covered here |
| Cross-browser (Chromium here; Firefox/WebKit via same fixtures) | Load/performance testing |

## 2. Risk-based prioritization
1. **Tenant data isolation** — highest business risk (security/compliance breach if broken).
2. **Login reliability** — blocks every other flow if flaky.
3. **Project creation consistency across surfaces** — core product value.

## 3. Test levels & tools
| Level | Tool | Files |
|---|---|---|
| API | `requests` + `pytest` | `api/`, `tests/integration/test_project_creation_flow.py` |
| UI (web) | Playwright (`pytest-playwright`) | `pages/`, `tests/test_login.py` |
| UI (mobile) | Playwright device emulation locally; BrowserStack real-device in CI | `tests/integration/test_project_creation_flow.py::test_mobile_accessibility_emulated` |

## 4. Environment & data strategy
- `TEST_ENV` selects `local` (mock server) / `staging` / `ci` via `config.py`.
- Credentials come from environment variables only — nothing sensitive is committed.
- Test data is generated per-run (UUID-suffixed project names) and self-cleans via API
  teardown in `conftest.py`, so parallel runs never collide and CI never accumulates junk data.

## 5. Assumptions (brief is intentionally incomplete)
- Auth: `POST /api/v1/auth/login` returns a bearer token; `X-Tenant-ID` scopes every
  API request and the backend enforces isolation server-side (403/404, not just UI hiding).
- "Mobile" means the responsive web app, not a separate native app — would confirm before
  investing in Appium.
- A `.project-card` element containing the project name exists on both desktop and mobile
  project list views.

## 6. Exit criteria
- All `smoke`-marked tests green on every PR; full `regression` suite green nightly.
- Zero known tenant-isolation failures — this class of bug blocks release regardless of
  anything else in the run.

## 7. Known limitation of this build
Playwright's browser binaries could not be downloaded in this sandboxed environment
(network is restricted to package registries and has no route to the Playwright CDN), so
the UI/mobile tests below are written and ready to run but were not executed here. The
API-layer tests were executed against the bundled mock server — see
`reports/TEST_EXECUTION_REPORT.md` for actual results.

"""Environment / tenant / credential config -- read at runtime, nothing hardcoded."""
import os

ENV = os.getenv("TEST_ENV", "local")

BASE_URLS = {
    "local": "http://localhost:5055",
    "staging": "https://staging.workflowpro.com",
    "ci": "https://ci.workflowpro.com",
}

UI_BASE_URL = os.getenv("WFP_UI_URL", BASE_URLS[ENV])
API_BASE_URL = os.getenv("WFP_API_URL", BASE_URLS[ENV])

TENANTS = {
    "company1": {
        "email": os.getenv("WFP_COMPANY1_ADMIN_EMAIL", "admin@company1.com"),
        "password": os.getenv("WFP_COMPANY1_ADMIN_PASSWORD", "password123"),
    },
    "company2": {
        "email": os.getenv("WFP_COMPANY2_USER_EMAIL", "user@company2.com"),
        "password": os.getenv("WFP_COMPANY2_USER_PASSWORD", "password123"),
    },
}

TEST_OTP = os.getenv("WFP_TEST_OTP", "123456")

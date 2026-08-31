"""Safe test configuration loaded before application modules."""

import os

os.environ.setdefault("REST_API_ENVIRONMENT", "test")
os.environ.setdefault("REST_API_JWT_SECRET", "test-secret-with-at-least-32-characters")

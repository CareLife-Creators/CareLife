"""Shared Selenium fixtures for deployed CareLife browser regression tests."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


DEFAULT_BASE_URL = "https://carelife-web.onrender.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the deployed frontend URL, allowing CI/review overrides."""
    return os.getenv("CARELIFE_E2E_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")


@pytest.fixture
def browser(request: pytest.FixtureRequest):
    """Start an isolated Chrome session and collect evidence when a test fails."""
    options = Options()
    options.add_argument("--window-size=1440,1100")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")

    headless = os.getenv("CARELIFE_HEADLESS", "true").strip().lower()
    if headless not in {"0", "false", "no"}:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(int(os.getenv("CARELIFE_PAGE_LOAD_TIMEOUT", "60")))
    driver.implicitly_wait(0)

    try:
        yield driver
    finally:
        driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Save browser evidence for failed tests so UI blockers are diagnosable."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = getattr(item, "funcargs", {}).get("browser")
    if driver is None:
        return

    output_dir = Path(os.getenv("CARELIFE_E2E_ARTIFACT_DIR", "test-results"))
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)

    try:
        driver.save_screenshot(str(output_dir / f"{safe_name}.png"))
    except Exception:
        pass

    try:
        (output_dir / f"{safe_name}.html").write_text(
            driver.page_source,
            encoding="utf-8",
        )
    except Exception:
        pass

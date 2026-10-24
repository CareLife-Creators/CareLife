"""Optional admin sign-in regression test for a dedicated test account."""

import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


ADMIN_EMAIL = os.getenv("CARELIFE_E2E_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("CARELIFE_E2E_PASSWORD", "")


@pytest.mark.skipif(
    not ADMIN_EMAIL or not ADMIN_PASSWORD,
    reason=(
        "Set CARELIFE_E2E_EMAIL and CARELIFE_E2E_PASSWORD to enable "
        "the deployed admin sign-in test."
    ),
)
def test_admin_can_sign_in(browser, base_url):
    browser.get(f"{base_url}/#login")
    wait = WebDriverWait(browser, 45)

    email_field = wait.until(
        EC.visibility_of_element_located((By.ID, "login-email"))
    )
    password_field = wait.until(
        EC.visibility_of_element_located((By.ID, "login-password"))
    )

    email_field.send_keys(ADMIN_EMAIL)
    password_field.send_keys(ADMIN_PASSWORD)
    browser.find_element(By.CSS_SELECTOR, "form.auth-form button[type='submit']").click()

    try:
        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), "Operations overview"
            )
        )
    except Exception as error:
        visible_text = browser.find_element(By.TAG_NAME, "body").text
        raise AssertionError(
            "Admin login did not reach the expected operations page.\n"
            f"Current URL: {browser.current_url}\n"
            f"Visible page text:\n{visible_text[:2500]}"
        ) from error

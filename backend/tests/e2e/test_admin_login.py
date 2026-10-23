import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = os.getenv("CARELIFE_E2E_BASE_URL", "http://127.0.0.1:5173")


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_admin_can_sign_in(browser):
    email = os.environ["CARELIFE_E2E_EMAIL"]
    password = os.environ["CARELIFE_E2E_PASSWORD"]

    browser.get(f"{BASE_URL}/#login")
    wait = WebDriverWait(browser, 30)

    email_field = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    password_field = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )

    email_field.send_keys(email)
    password_field.send_keys(password)

    # Submit the form through its normal submit handler.
    login_form = browser.find_element(By.CSS_SELECTOR, "form")
    browser.execute_script("arguments[0].requestSubmit()", login_form)

    try:
        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), "Operations overview"
            )
        )
    except Exception as error:
        visible_text = browser.find_element(By.TAG_NAME, "body").text
        raise AssertionError(
            f"Admin login did not reach the expected page.\n"
            f"Current URL: {browser.current_url}\n"
            f"Visible page text:\n{visible_text}"
        ) from error

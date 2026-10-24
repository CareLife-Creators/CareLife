import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = os.getenv("CARELIFE_E2E_BASE_URL", "http://127.0.0.1:5173")


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1365,900")
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def test_signup_page_loads_in_browser(browser):
    browser.get(f"{BASE_URL}/#signup")

    WebDriverWait(browser, 20).until(
        lambda driver: "Create your account"
        in driver.find_element(By.TAG_NAME, "body").text
    )

    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "Parent or guardian" in page_text
    assert "Donor or supporter" in page_text

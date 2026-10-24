"""Selenium smoke and regression checks against the deployed CareLife UI."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_homepage_renders(browser, base_url):
    browser.get(f"{base_url}/#home")
    wait = WebDriverWait(browser, 45)

    hero = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".lp-hero h1"))
    )

    assert "Care you can count on" in hero.text
    assert "CareLife" in browser.title
    assert browser.find_elements(By.CSS_SELECTOR, 'button[aria-label="CareLife home"]') or browser.find_elements(
        By.CSS_SELECTOR, 'a[aria-label="CareLife home"]'
    )


def test_signup_page_and_roles_render(browser, base_url):
    browser.get(f"{base_url}/#signup")
    wait = WebDriverWait(browser, 30)

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[normalize-space()='Create your account']")
        )
    )

    for field_id in ("signup-name", "signup-email", "signup-phone"):
        field = browser.find_element(By.ID, field_id)
        assert field.is_displayed(), f"Expected signup field #{field_id}"
        assert field.get_attribute("required") is not None

    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "Parent or guardian" in page_text
    assert "Donor or supporter" in page_text
    assert "Independent caregiver" in page_text


def test_signup_required_fields_use_browser_validation(browser, base_url):
    browser.get(f"{base_url}/#signup")
    wait = WebDriverWait(browser, 30)
    form = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form.auth-form"))
    )

    # This only checks native client-side validation; it does not create an account.
    assert browser.execute_script("return arguments[0].checkValidity()", form) is False


def test_login_and_password_reset_pages_render(browser, base_url):
    browser.get(f"{base_url}/#login")
    wait = WebDriverWait(browser, 30)

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[normalize-space()='Sign in to CareLife']")
        )
    )

    assert browser.find_element(By.ID, "login-email").is_displayed()
    assert browser.find_element(By.ID, "login-password").is_displayed()

    # The app briefly renders a loader over the form during route/session checks.
    wait.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".cl-loader"))
    )
    forgot_password = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.forgot-password"))
    )
    forgot_password.click()
    wait.until(lambda driver: "#password-reset" in driver.current_url)

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[normalize-space()='Reset your password']")
        )
    )
    assert browser.find_element(By.ID, "reset-email").is_displayed()


@pytest.mark.parametrize(
    "route",
    ["#daycare", "#orphanage", "#elderly-care"],
)
def test_care_module_landing_pages_open_without_sign_in(browser, base_url, route):
    browser.get(f"{base_url}/{route}")
    wait = WebDriverWait(browser, 30)

    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))
    heading = browser.find_element(By.TAG_NAME, "h1")

    assert heading.text.strip(), f"Expected a heading on {route}"
    assert route in browser.current_url, (
        f"Expected to remain on {route}; current URL is {browser.current_url}"
    )


@pytest.mark.parametrize(
    ("route", "selector"),
    [
        ("#daycare-directory", "main.daycare-directory"),
        ("#elderly-care-directory", "main.directory-page.elder"),
        ("#caregivers", "main.directory-page.caregiver"),
        ("#orphanage-support", "main.directory-page.orphanage"),
    ],
)
def test_public_discovery_pages_open_without_sign_in(
    browser, base_url, route, selector
):
    """Verify public directory/support pages are not sent to the login screen."""
    browser.get(f"{base_url}/{route}")
    wait = WebDriverWait(browser, 30)

    wait.until(
        lambda driver: driver.find_elements(By.CSS_SELECTOR, selector)
        or "#login" in driver.current_url
    )

    assert browser.find_elements(By.CSS_SELECTOR, selector), (
        f"Expected {route} to be publicly accessible, but the browser ended at "
        f"{browser.current_url}. Visible page text: "
        f"{browser.find_element(By.TAG_NAME, 'body').text[:1200]}"
    )

"""Selenium regression checks against the currently deployed CareLife UI."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


PUBLIC_DISCOVERY_PAGES = [
    ("#daycare-directory", "main.daycare-directory"),
    ("#elderly-care-directory", "main.directory-page.elder"),
    ("#caregivers", "main.directory-page.caregiver"),
    ("#orphanage-support", "main.directory-page.orphanage"),
]

PRIVATE_SIGNED_OUT_ROUTES = [
    "#dashboard",
    "#my-children",
    "#family-checkins",
    "#care-bookings",
    "#messages",
    "#account",
    "#organization-workspace",
    "#admin-operations",
]


def test_homepage_renders(browser, base_url):
    browser.get(f"{base_url}/#home")
    wait = WebDriverWait(browser, 45)

    hero = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".lp-hero h1"))
    )

    assert "Care you can count on" in hero.text
    assert "CareLife" in browser.title
    assert (
        browser.find_elements(By.CSS_SELECTOR, 'button[aria-label="CareLife home"]')
        or browser.find_elements(By.CSS_SELECTOR, 'a[aria-label="CareLife home"]')
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
    assert "Family representative" in page_text


def test_signup_required_fields_use_browser_validation(browser, base_url):
    browser.get(f"{base_url}/#signup")
    wait = WebDriverWait(browser, 30)
    form = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form.auth-form"))
    )

    # Check native validation only; do not create an account or submit personal data.
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

    # The app can briefly put a loader above the login form while checking a session.
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


@pytest.mark.parametrize("route", ["#daycare", "#orphanage", "#elderly-care"])
def test_care_module_landing_pages_open_without_sign_in(browser, base_url, route):
    browser.get(f"{base_url}/{route}")
    wait = WebDriverWait(browser, 30)

    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))
    heading = browser.find_element(By.TAG_NAME, "h1")
    assert heading.text.strip(), f"Expected a heading on {route}"
    assert route in browser.current_url, (
        f"Expected to remain on {route}; current URL is {browser.current_url}"
    )


@pytest.mark.parametrize(("route", "selector"), PUBLIC_DISCOVERY_PAGES)
def test_public_discovery_pages_open_without_sign_in(
    browser, base_url, route, selector
):
    """Public listings and support pages must not redirect visitors to sign-in."""
    browser.get(f"{base_url}/{route}")
    wait = WebDriverWait(browser, 40)

    # Stop waiting once the intended page appears or the old protected-route
    # behavior is detected, so a route regression produces a useful assertion.
    wait.until(
        lambda driver: driver.find_elements(By.CSS_SELECTOR, selector)
        or "#login" in driver.current_url
    )

    page = browser.find_elements(By.CSS_SELECTOR, selector)
    assert page, (
        f"Expected {route} to be public, but the browser ended at "
        f"{browser.current_url}. Visible page text: "
        f"{browser.find_element(By.TAG_NAME, 'body').text[:1600]}"
    )
    heading = page[0].find_element(By.CSS_SELECTOR, "h1")
    assert heading.is_displayed() and heading.text.strip(), (
        f"Expected a visible page heading on {route}"
    )


@pytest.mark.parametrize("route", PRIVATE_SIGNED_OUT_ROUTES)
def test_private_account_and_record_routes_require_sign_in(
    browser, base_url, route
):
    """Private records, workspaces and account pages remain protected."""
    browser.get(f"{base_url}/{route}")
    wait = WebDriverWait(browser, 30)

    wait.until(
        lambda driver: "#login" in driver.current_url
        and driver.find_elements(By.ID, "login-email")
    )

    assert "#login" in browser.current_url, (
        f"{route} should redirect a signed-out visitor to login; "
        f"current URL is {browser.current_url}"
    )
    assert browser.find_element(By.ID, "login-password").is_displayed()


def test_signed_out_support_board_hides_personal_donation_history(
    browser, base_url
):
    """Personal pledge and payment tabs should only appear for signed-in donors."""
    browser.get(f"{base_url}/#orphanage-support")
    wait = WebDriverWait(browser, 40)

    tabs_or_login = wait.until(
        lambda driver: driver.find_elements(
            By.CSS_SELECTOR, "main.directory-page.orphanage .support-tabs"
        )
        or "#login" in driver.current_url
    )
    if "#login" in browser.current_url:
        pytest.fail(
            "The public support board redirected a signed-out visitor to login "
            f"instead of rendering its tabs. Current URL: {browser.current_url}. "
            f"Visible page text: {browser.find_element(By.TAG_NAME, 'body').text[:1200]}"
        )

    tabs = tabs_or_login[0] if isinstance(tabs_or_login, list) else tabs_or_login
    labels = [
        tab.text.strip()
        for tab in tabs.find_elements(By.CSS_SELECTOR, '[role="tab"]')
    ]

    assert "Campaigns" in labels
    assert "In-kind needs" in labels
    assert "Impact updates" in labels
    assert "My item pledges" not in labels
    assert "My payments" not in labels

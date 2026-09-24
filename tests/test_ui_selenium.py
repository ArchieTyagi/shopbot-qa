# test_ui_selenium.py
# Web UI tests with Selenium: a robot opens Chrome and uses the site like a real person.
#
# You will SEE Chrome open and click by itself when you run this on your laptop.
# On GitHub Actions (no screen) it runs "headless" = invisible.

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.getenv("CI"):  # GitHub Actions sets CI=true
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    if os.getenv("CHROME_BIN"):
        options.binary_location = os.getenv("CHROME_BIN")

    driver = webdriver.Chrome(options=options)
    yield driver  # give the browser to the test
    if os.getenv("SLOW"):  # run with SLOW=1 to pause and watch the result
        time.sleep(4)
    driver.quit()  # close it after the test


def wait_for(driver, by, value):
    """Wait up to 5 seconds for an element to be visible. Avoids flaky tests."""
    return WebDriverWait(driver, 5).until(EC.visibility_of_element_located((by, value)))


def login(driver, base_url, username, password):
    driver.get(base_url)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def test_login_success(driver, base_url):
    login(driver, base_url, "archi", "test123")
    welcome = wait_for(driver, By.ID, "welcome")
    assert "Welcome, archi" in welcome.text


def test_login_wrong_password_shows_error(driver, base_url):
    login(driver, base_url, "archi", "wrong")
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.ID, "login-error"), "Wrong")
    )
    assert driver.find_element(By.ID, "login-error").text == "Wrong username or password"


def test_products_are_shown_after_login(driver, base_url):
    login(driver, base_url, "archi", "test123")
    wait_for(driver, By.CLASS_NAME, "product")
    products = driver.find_elements(By.CLASS_NAME, "product")
    assert len(products) == 3
    assert "Headphones" in products[0].text


def test_chat_from_the_website(driver, base_url):
    login(driver, base_url, "archi", "test123")
    chat_box = wait_for(driver, By.ID, "chat-input")
    chat_box.send_keys("What is the price of keyboard?")
    driver.find_element(By.ID, "chat-send").click()

    reply = wait_for(driver, By.CLASS_NAME, "bot-reply")
    assert "1499" in reply.text

import pytest
import allure
from helpers.locators import Locators
import helpers.constants as const
import time as t
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@allure.title('Verify FS events in the Cart workflow')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.E2E
def test_cart_workflow(setup):
    with allure.step('Launch the test application'):
        driver = setup
        driver.get(const.BASE_URL)
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.mangocados_css_selector)))

    with allure.step('Add the featured fruit Mangocados to cart and verify mouse click is captured by FS'):
        driver.find_element_by_css_selector(Locators.mangocados_css_selector).click()

        # wait till bundle requests are generated
        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=2', 20)
        t.sleep(10)

        bundle_requests = [json.loads(request.body) for request in driver.requests if
                           "rs.fullstory.com/rec/bundle" in request.url]

        click_event_found = False
        custom_event_found = False
        for bundle_request in bundle_requests:
            for event in bundle_request['Evts']:
                if event['Kind'] == const.CLICK_EVENT:
                    click_event_found = True
                if event['Kind'] == const.CUSTOM_EVENT:
                    custom_event_found = "Mangocados" in json.loads(event['Args'][1])['displayName_str']

        assert click_event_found, "Click event is not found"
        assert custom_event_found, "Mangocados is not added to the cart"

    with allure.step('Go to cart and verify the navigation to cart page event is captured by FS'):
        driver.find_element_by_css_selector(Locators.cart_css_selector).click()
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.go_checkout_css_selector)))

        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=4', 35)

        bundle_requests = [json.loads(request.body) for request in driver.requests if
                           "rs.fullstory.com/rec/bundle" in request.url]

        go_to_cart_event_found = False
        for bundle_request in bundle_requests:
            for event in bundle_request['Evts']:
                if event['Kind'] == const.NAVIGATE_EVENT:
                    if event['Args'][0] == "https://fruitshoppe.firebaseapp.com/#/cart":
                        go_to_cart_event_found = True

        assert go_to_cart_event_found, "Go to cart event is not found"

    with allure.step('Go to checkout'):
        driver.find_element_by_css_selector(Locators.go_checkout_css_selector).click()
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, Locators.first_name_id)))

    with allure.step(
            'Provide the required details for shipping and payment and verify credit card number and CVV are not captured by FS before checkout'):
        driver.find_element_by_id(Locators.first_name_id).send_keys('firstname')
        driver.find_element_by_id(Locators.last_name_id).send_keys('lastname')
        driver.find_element_by_id(Locators.address_1_id).send_keys('address1')
        driver.find_element_by_id(Locators.address_2_id).send_keys('address2')
        driver.find_element_by_id(Locators.billing_city_id).send_keys('Knoxville')
        driver.find_element_by_id(Locators.zip_id).send_keys('37932')
        driver.find_element_by_id(Locators.credit_card_number_id).send_keys(const.CREDIT_CARD_NUMBER)
        driver.find_element_by_id(Locators.cvv_id).send_keys(const.CREDIT_CARD_CVV)

        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=6', 35)
        bundle_requests = "".join(
            [str(request.body) for request in driver.requests if "rs.fullstory.com/rec/bundle" in request.url])

        assert const.CREDIT_CARD_NUMBER not in bundle_requests, "Credit card number is found in the events"

        driver.find_element_by_id(Locators.im_sure_check_id).click()

        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.checkout_css_selector)))

    with allure.step('Checkout the item and verify credit card number and CVV are not captured by FS after checkout'):
        driver.find_element_by_css_selector(Locators.checkout_css_selector).click()

        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=7', 40)
        bundle_requests = "".join(
            [str(request.body) for request in driver.requests if "rs.fullstory.com/rec/bundle" in request.url])

        assert const.CREDIT_CARD_NUMBER not in bundle_requests, "Credit card number is found in the events"


@allure.title('Verify heartbeat events are sent even in user inactivity state')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.smoke
def test_user_inactivity(setup):
    with allure.step('Launch the test application'):
        driver = setup
        driver.get(const.BASE_URL)
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.mangocados_css_selector)))
        t.sleep(10)

        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=2', 40)

        bundle_requests = [json.loads(request.body) for request in driver.requests if
                           "rs.fullstory.com/rec/bundle" in request.url]

        heart_beat_event_found = False
        for bundle_request in bundle_requests:
            for event in bundle_request['Evts']:
                if event['Kind'] == const.HEART_BEAT_EVENT:
                    heart_beat_event_found = True

        assert heart_beat_event_found, "Heart beat event is not found"

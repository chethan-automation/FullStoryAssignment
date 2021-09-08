import pytest
import allure
from helpers.locators import Locators
import helpers.constants as const
import helpers.utils as utils
import json
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@allure.title('Verify network events in the Cart workflow')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.E2E
def test_cart_workflow(setup):
    with allure.step('Launch the test application'):
        driver = setup
        driver.get(const.BASE_URL)
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.mangocados_css_selector)))

    with allure.step('Add the featured fruit Mangocados to cart and verify mouse click is captured by the aplication'):
        utils.initial_wait_for_requests(driver)
        seq = utils.get_last_seq(driver)

        driver.find_element_by_css_selector(Locators.mangocados_css_selector).click()

        utils.wait_for_bundle_requests(driver, seq, 2)

        assert utils.validate_event(driver, const.CLICK_EVENT), "Click event is not found"
        assert utils.validate_event(driver, const.CUSTOM_EVENT, "Mangocados"), "Mangocados is not added to the cart"

    with allure.step('Go to cart and verify the navigation to cart page event is captured by the application'):
        seq = utils.get_last_seq(driver)

        driver.find_element_by_css_selector(Locators.cart_css_selector).click()
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.go_checkout_css_selector)))

        utils.wait_for_bundle_requests(driver, seq, 1)

        assert utils.validate_event(driver, const.NAVIGATE_EVENT,
                                    "https://fruitshoppe.firebaseapp.com/#/cart"), "Go to cart event is not found"

    with allure.step('Go to checkout'):
        driver.find_element_by_css_selector(Locators.go_checkout_css_selector).click()
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, Locators.first_name_id)))

    with allure.step(
            'Provide the required details for shipping and payment and verify credit card number and CVV are not captured by the application before checkout'):
        driver.find_element_by_id(Locators.first_name_id).send_keys('firstname')
        driver.find_element_by_id(Locators.last_name_id).send_keys('lastname')
        driver.find_element_by_id(Locators.address_1_id).send_keys('address1')
        driver.find_element_by_id(Locators.address_2_id).send_keys('address2')
        driver.find_element_by_id(Locators.billing_city_id).send_keys('Knoxville')

        billing_state = Select(driver.find_element_by_id("billing-state"))
        billing_state.select_by_visible_text('TN')

        driver.find_element_by_id(Locators.zip_id).send_keys('37932')
        driver.find_element_by_id(Locators.shipping_same_billing_id).click()
        driver.find_element_by_id(Locators.credit_card_number_id).send_keys(const.CREDIT_CARD_NUMBER)
        driver.find_element_by_id(Locators.cvv_id).send_keys(const.CREDIT_CARD_CVV)
        driver.find_element_by_id(Locators.im_sure_check_id).click()

        seq = utils.get_last_seq(driver)
        utils.wait_for_bundle_requests(driver, seq, 1)

        assert not utils.is_text_present_in_requests(driver,
                                                     const.CREDIT_CARD_NUMBER), "Credit card number is found in the events"

    with allure.step('Checkout the item and verify credit card number and CVV are not captured by the application after checkout'):
        seq = utils.get_last_seq(driver)

        driver.find_element_by_css_selector(Locators.checkout_css_selector).click()

        utils.wait_for_bundle_requests(driver, seq, 1)

        assert not utils.is_text_present_in_requests(driver,
                                                     const.CREDIT_CARD_NUMBER), "Credit card number is found in the events"


@allure.title('Verify heartbeat events are sent even in user inactivity state')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.smoke
def test_user_inactivity(setup):
    with allure.step('Launch the test application'):
        driver = setup
        driver.get(const.BASE_URL)
        WebDriverWait(driver, const.DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.mangocados_css_selector)))

        driver.wait_for_request('rs.fullstory.com/rec/bundle.*?Seq=2', 40)

        bundle_requests = [json.loads(request.body) for request in driver.requests if
                           "rs.fullstory.com/rec/bundle" in request.url]

        heart_beat_event_found = False
        for bundle_request in bundle_requests:
            for event in bundle_request['Evts']:
                if event['Kind'] == const.HEART_BEAT_EVENT:
                    heart_beat_event_found = True

        assert heart_beat_event_found, "Heart beat event is not found"

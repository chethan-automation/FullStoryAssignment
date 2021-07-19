import pytest
import allure
from helpers.locators import Locators
import helpers.constants as const
import time as t
import json


@allure.title('Verify FS events in the Cart workflow')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.sanity
def test_cart_workflow(setup):
    with allure.step('Launch the test application'):
        driver = setup
        driver.get(const.BASE_URL)
        t.sleep(5)

    with allure.step('Add the featured fruit Mangocados to cart'):
        driver.find_element_by_css_selector(Locators.mangocados_css_selector).click()
        # for request in driver.requests:
        #     if "rs.fullstory.com/rec/bundle" in request.url:
        #         print(request.body)

        # list comprehensive
        t.sleep(3)
        bundle_requests = [json.loads(request.body) for request in driver.requests if
                           "rs.fullstory.com/rec/bundle" in request.url]

        click_event_found = False
        custom_event_found = False
        for bundle_request in bundle_requests:
            for event in bundle_request['Evts']:
                if event['Kind'] == 16:
                    click_event_found = True
                if event['Kind'] == 8197:
                    custom_event_found = "Mangocados" in json.loads(event['Args'][1])['displayName_str']

        assert click_event_found, "Click event is not found"
        assert custom_event_found, "Mangocados is not added to the cart"

    with allure.step('Go to cart'):
        driver.find_element_by_css_selector(Locators.cart_css_selector).click()
        t.sleep(3)

    with allure.step('Go to checkout'):
        driver.find_element_by_css_selector(Locators.go_checkout_css_selector).click()
        t.sleep(5)

    with allure.step('Provide the required details for shipping and payment'):
        driver.find_element_by_id(Locators.first_name_id).send_keys('firstname')
        driver.find_element_by_id(Locators.last_name_id).send_keys('lastname')
        driver.find_element_by_id(Locators.address_1_id).send_keys('address1')
        driver.find_element_by_id(Locators.address_2_id).send_keys('address2')
        driver.find_element_by_id(Locators.billing_city_id).send_keys('Knoxville')
        driver.find_element_by_id(Locators.zip_id).send_keys('37932')
        driver.find_element_by_id(Locators.credit_card_number_id).send_keys('1111222233334444')
        driver.find_element_by_id(Locators.cvv_id).send_keys('333')

        driver.find_element_by_id(Locators.im_sure_check_id).click()
        t.sleep(2)

    with allure.step('Checkout the item'):
        driver.find_element_by_css_selector(Locators.checkout_css_selector).click()

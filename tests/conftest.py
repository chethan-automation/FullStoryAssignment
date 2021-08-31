import pytest
from seleniumwire import webdriver
import os


@pytest.fixture(scope="function")
def setup():
    # Create a driver
    driver = webdriver.Chrome(os.path.abspath("drivers/chromedriver"))
    # Return the driver object by the end of the setup
    yield driver
    # For cleanup, quit the driver instance
    driver.quit()


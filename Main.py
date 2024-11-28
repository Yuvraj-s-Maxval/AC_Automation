import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create the logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create a timestamped log file name
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(log_dir, f"automation_{timestamp}.log")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Log to a timestamped file in the logs directory
        logging.StreamHandler()        # Log to the console
    ]
)

class AppCollAutomation:
    def __init__(self, driver_path):
        logging.info("Initializing AppCollAutomation.")
        self.root_url = "https://login.appcoll.com/"
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
        self.chrome_options.add_argument("--start-maximized")  # Maximize the window on startup
        self.service = Service(driver_path)  # Driver path is passed as an argument
        self.driver = None

    def start_browser(self):
        logging.info("Starting the browser.")
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            logging.info("Browser started successfully.")
        except Exception as e:
            logging.error(f"Error starting browser: {e}")
            raise

    def perform_actions(self, login_id, login_pass):
        try:
            logging.info("Opening the website.")
            self.driver.get(self.root_url)
            self.driver.implicitly_wait(10)

            # Login
            logging.info("Attempting to log in.")
            login_username_element = self.driver.find_element(By.XPATH, '//input[@id="LoginBox_UserName"]')
            login_password_element = self.driver.find_element(By.XPATH, '//input[@id="LoginBox_Password"]')
            login_button_element = self.driver.find_element(By.XPATH, '//input[@id="LoginBox_LoginButton"]')

            # Clear and enter username and password
            login_username_element.clear()
            login_password_element.clear()
            logging.info("Entering username and password.")
            login_username_element.send_keys(login_id)
            login_password_element.send_keys(login_pass)

            # Click the login button
            logging.info("Clicking the login button.")
            login_button_element.click()

            # Wait for the submit button to appear and click it
            logging.info("Waiting for the submit button to appear.")
            submit_button_element = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="ContactMethodSubmitButton"]'))
            )
            logging.info("Submit button appeared. Clicking the submit button.")
            submit_button_element.click()

            logging.info("Submit button clicked successfully.")

            # Wait for the URL to change to the 'Tasks' page (after entering the code)
            WebDriverWait(self.driver, 120).until(
                lambda driver: driver.current_url == "https://login.appcoll.com/Tasks.aspx"
            )
            logging.info("Redirected to the Tasks page after authorization.")

            # Wait for the "Columns" button to be clickable
            columns_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@id="ctl00_ChooseColumnsButton"]'))
            )

            # If the button is found, log and print a message
            if columns_button:
                logging.info("Columns button found.")
                print("Columns button found.")
                columns_button.click()  # Click the button if it's found
            else:
                logging.error("Columns button not found.")

        except Exception as e:
            logging.error(f"An error occurred during the process: {e}")
            raise

    def close_browser(self):
        logging.info("Closing the browser.")
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed successfully.")

# Example usage
if __name__ == "__main__":
    driver_path = "Drivers/chromedriver.exe"
    automation = AppCollAutomation(driver_path)

    try:
        automation.start_browser()  # Start the browser
        automation.perform_actions("faisal@bochner.law", "Maxval@2024")  # Replace with actual credentials
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        automation.close_browser()  # Close the browser

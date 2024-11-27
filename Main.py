from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep

class AppCollAutomation:
    def __init__(self, driver_path):

        # Initialize the driver and set up options
        self.root_url = "https://www.appcoll.com/"
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--start-maximized")  # Maximize the window on startup
        self.service = Service(driver_path)  # Driver path is passed as an argument
        self.driver = None

    def start_browser(self):
        # Start the WebDriver
        self.driver = webdriver.Chrome(
            service=self.service, options=self.chrome_options
        )

    def open_website(self):
        # Opening the main website
        self.driver.get(self.root_url)
        self.driver.implicitly_wait(10)  # Wait for the page to load completely

        # Wait for 5 seconds
        sleep(5)

    def close_browser(self):
        # Close the browser after operation
        if self.driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    driver_path = "Drivers/chromedriver.exe"
    automation = AppCollAutomation(driver_path)

    automation.start_browser()  # Start the browser
    automation.open_website()   # Open the website and wait for 5 seconds
    automation.close_browser()  # Close the browser

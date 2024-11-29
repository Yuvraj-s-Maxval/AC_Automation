import logging
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from tkinter import Tk, filedialog  # Import tkinter for file dialog

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
    def __init__(self, driver_path, download_directory):
        logging.info("Initializing AppCollAutomation.")
        self.root_url = "https://login.appcoll.com/"
        
        # Set Chrome options to specify download folder
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")  # Maximize the window on startup
        self.chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_directory,  # Set custom download path
            "download.prompt_for_download": False,  # Don't prompt for download location
            "directory_upgrade": True,  # Allows overwriting files in the download directory
            "safebrowsing.enabled": True  # Disable the safe browsing feature to prevent blocking downloads
        })
        
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

    # Retry mechanism for clicking the AddColumn button
    def click_add_column(self):
        try:
            add_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@onclick='AddColumn();']"))
            )
            add_button.click()
            logging.info("Column added successfully.")
        except StaleElementReferenceException as e:
            logging.warning("StaleElementReferenceException occurred. Retrying...")
            time.sleep(2)  # Optional: wait for a short period before retrying
            self.click_add_column()  # Retry the click operation


    def data_filtering(self,df):
        """
        This function filters the input DataFrame based on specific conditions and returns two DataFrames: one for patent-related data and another for trademark-related data.

        Parameters:
        - df (DataFrame): The input DataFrame to be filtered.

        Returns:
        - patent_df (DataFrame): A DataFrame containing patent-related data after filtering.
        - trademark_df (DataFrame): A DataFrame containing trademark-related data after filtering.

        The filtering process involves the following steps:
        1. Remove rows where 'DeadlineType' is 'Internal Deadline'.
        2. Iterate over each row to check for specific conditions in 'Owner', 'Matter.Title', 'Matter.Type', and 'TaskType' columns.
        3. If any of the conditions are met, the index of that row is added to a list of indexes to be filtered.
        4. Drop rows based on the list of indexes.
        5. Create a patent_df by dropping 'Matter.Title' column from the filtered DataFrame.
        6. Create a trademark_df as a copy of the filtered DataFrame.
        """
        # Removing the internal deadlines
        df = df[df['DeadlineType'] != 'Internal Deadline']
        df = df.reset_index(drop=True)

        indexes_filtered = []

        # Iterating over the Owner column to look for Brittany Steele
        for i in range(len(df)):

            # Extracting the owner and the Matter title
            owner = df.at[i,'Owner']
            matter_title = df.at[i,'Matter.Title']
            matter_type = df.at[i, 'Matter.Type']
            task_type = df.at[i,'TaskType']
            
            if owner == 'Brittany Steele' or owner == 'Faisal Khan' or 'FTO' in matter_title or 'review' in task_type.lower() or 'trademark: opposition' in matter_type.lower():
                
                # Adding the index
                indexes_filtered.append(i)

        df = df.drop(indexes_filtered)
        df.reset_index(drop=True)
        
        patent_df = df.drop(['Matter.Title'],axis=1)
        trademark_df = df.copy()
        patent_df.to_csv("data/patent_data.csv")
        trademark_df.to_csv("data/trademark_data.csv")
        logging.info("Csv files processed succesfully")

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
            
            # Check if the "Columns" button exists
            if columns_button:
                logging.info("Columns button found.")
                columns_button.click()  # Click the button if it's found

                # List of required columns
                required_columns = [
                    'TaskStatus', 'Matter', 'Matter.Title', 'Matter.Type',
                    'TaskType', 'DeadlineType', 'Owner', 'Comments'
                ]

                # Loop until all required columns are processed
                while required_columns:
                    # Locate the dropdown again to get updated options
                    all_columns = self.driver.find_element(By.XPATH, "//select[@id='ctl00_UnselectedColumnsList']")
                    all_columns_select = Select(all_columns)

                    # Track whether a column was added in this iteration
                    column_added = False

                    # Iterate through each option in the dropdown
                    for option in all_columns_select.options:
                        if option.text in required_columns:
                            logging.info(f"Found matching column: {option.text}")
                            print(f"Found matching column: {option.text}")

                            # Select the matching column
                            all_columns_select.select_by_visible_text(option.text)

                            # # Wait for and click the "AddColumn" button, with retry logic
                            # self.click_add_column()

                            # Remove the column from the required list
                            required_columns.remove(option.text)

                            # Log the action
                            logging.info(f"{option.text} column added")
                            print(f"{option.text} column added")

                            # Indicate a column was added and break to re-fetch the dropdown
                            column_added = True
                            break

                    # If no column was added in this iteration, break the loop
                    if not column_added:
                        logging.info("No matching columns found in the dropdown.")
                        print("No matching columns found in the dropdown.")
                        break

                    
                required_columns = [
                    'TaskStatus', 'Matter', 'Matter.Title', 'Matter.Type',
                    'TaskType', 'DeadlineType', 'Owner', 'Comments'
                ]
                
                selected_columns_element = self.driver.find_element(By.XPATH, "//select[@id='ctl00_SelectedColumnsList']")
                selected_columns_select = Select(selected_columns_element)
                all_required_columns_exist = all(option.text in required_columns for option in selected_columns_select.options)
                if all_required_columns_exist:
                    logging.info("All required columns exist in the selected columns.")
                    WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@id="ctl00_ChooseColumnsOk"]'))).click()
                    logging.info("Required columns selected")

                    # Exporting the file as CSV file
                    logging.info("Exporting the CSV file.")
                    WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@title="Export information to CSV file"]'))).click()
                    WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@value="Export"]'))).click()
                    
                    logging.info("Export triggered, waiting for file download...")
                    
                    # Here, we invoke a temporary UI for file selection after export
                    self.prompt_for_file_input()

                else:
                    logging.error("Not all required columns exist in the selected columns.")
                time.sleep(10)
            else:
                logging.error("Columns button not found.")

        except Exception as e:
            logging.error(f"An error occurred during the process: {e}")
            raise

    def prompt_for_file_input(self):
        """ Use tkinter to create a temporary UI to prompt the user to select the downloaded file. """
        logging.info("Opening file dialog for user to select the downloaded CSV file.")
        
        # Creating a tkinter root window (hidden, since we just want the file dialog)
        root = Tk()
        root.withdraw()  # Hide the root window

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select the downloaded CSV file", 
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if file_path:
            logging.info(f"File selected: {file_path}")
            # Continue with the process using the selected file
            self.process_downloaded_file(file_path)
        else:
            logging.warning("No file selected. Proceeding without file.")
        
        root.quit()  # Close the tkinter window

    def process_downloaded_file(self, file_path):
        """ Continue with processing the downloaded file (e.g., reading, analyzing, etc.) """
        logging.info(f"Processing the file at {file_path}...")
        # Add your file processing logic here (e.g., reading CSV, parsing data, etc.)
        time.sleep(3)  # Simulating file processing time
        logging.info(f"File {file_path} processed successfully.")

    def close_browser(self):
        logging.info("Closing the browser.")
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed successfully.")

# Example usage
if __name__ == "__main__":
    driver_path = "Drivers/chromedriver.exe"
    download_directory = "path/to/your/download/folder"  # Adjust this path
    automation = AppCollAutomation(driver_path, download_directory)

    try:
        automation.start_browser()  # Start the browser
        automation.perform_actions("faisal@bochner.law", "Maxval@2024")  # Replace with actual credentials
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        automation.close_browser()  # Close the browser

from datetime import datetime
from glob import glob
import os
import pandas as pd
import time

from pathlib import Path
from selenium import webdriver
from chromedriver_py import binary_path
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm

def init_driver(local_download_path):
    os.makedirs(local_download_path, exist_ok=True)
    
    # Set up the driver
    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc)

    # Set up the Chrome options so that any CSV downloads are saved to project dir
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow','downloadPath':local_download_path}}
    command_result = driver.execute("send_command", params)

    return driver

def submit_election(driver, homepage, election):

    # Open the webpage
    driver.get(homepage)

    # Wait for the dropdown to be loaded (change the wait time as necessary)
    wait = WebDriverWait(driver, 2)
    wait.until(EC.element_to_be_clickable((By.ID, 'idElection')))

    # Select the election from the dropdown by visible text
    dropdown_element = driver.find_element(By.ID, 'idElection')  # Updated to the new method
    select = Select(dropdown_element)
    select.select_by_visible_text(election)

    # Click the submit button
    submit_button = driver.find_element(By.XPATH, '//button[@onclick="return submitForm();"]')
    submit_button.click()
    return driver

def get_selected_ev_date_dropdown(driver, dropdown_name = 'Official Early Voting Turnout by Date'):
    wait = WebDriverWait(driver, 2)
    dropdown_container = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(), '{dropdown_name}')]")))
    dropdown_element = dropdown_container.find_element(By.XPATH, "./following-sibling::div//select[@id='selectedDate']")
    select = Select(dropdown_element)
    return select

def get_report_dates(driver, origin_url, election):    
    # navigate to the election page to see dates of eligible reports
    driver = submit_election(driver, origin_url, election)

    # Locate the parent div by checking for unique text within, then find the dropdown within this div
    select = get_selected_ev_date_dropdown(driver)
    dates = [option.text.strip() for option in select.options][1:]  # w/o 'Select Early Voting Date'
    return dates



if __name__ == "__main__":
    # Constants/Params (election should be configurable)
    ORIGIN_URL = "https://earlyvoting.texas-election.com/Elections/getElectionDetails.do"
    ELECTION = '2024 MARCH 5TH DEMOCRATIC PRIMARY'
    CSV_DL_DIR = "downloaded_files"

    # initialize the driver (mainly to ensure CSVs we download stay in this project folder)    
    driver = init_driver(local_download_path=CSV_DL_DIR)

    # clear local downloads folder before beginning 
    # (later we use count of files in this folder to determine when a new file has finished 
    #  downloading and is ready to be renamed; so we need to start with a clean slate)
    for f in os.listdir(CSV_DL_DIR):
        fpath = os.path.join(CSV_DL_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)

    # Get report-dates we'll need to iterate through
    report_dates = get_report_dates(driver, ORIGIN_URL, ELECTION)

    num_csvs_downloaded = 0
    for d in report_dates:
        print(f"Downloading report for {d}")
        # navigate back to the main Early Voter page for this election 
        driver = submit_election(driver, ORIGIN_URL, ELECTION)

        # Select current date from dropdown
        select = get_selected_ev_date_dropdown(driver)
        select.select_by_visible_text(d)

        # Click the submit button for fetching table of EV detailed data
        time.sleep(3)
        driver.execute_script("validateSubmit();")

        # Click the "Generate Report" button to download as a csv
        # ...unless we got a pop-up saying there's no data for this date
        print(f"Executing downloadReport() button / js script")
        DOWNLOAD_WAIT_SECONDS = 5
        try:
            driver.execute_script("downloadReport('');")
            WebDriverWait(driver, DOWNLOAD_WAIT_SECONDS).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Alert text: {alert.text}")
            alert.accept()
        except TimeoutException:
            print(f"No alert found after {DOWNLOAD_WAIT_SECONDS} seconds; attempting to process file download")

            # Wait for the download to complete
            num_csvs_downloaded += 1
            while len([f for f in os.listdir(CSV_DL_DIR) if f.endswith('.csv')]) < num_csvs_downloaded:
                print(f"waiting for {d} to download...")
                time.sleep(1)

            # rename that downloaded file to include the date, so we know which file is which later
            csv_files = [f for f in os.listdir(CSV_DL_DIR) if f.endswith('.csv')]
            print(csv_files)       
            latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(CSV_DL_DIR, x)))
            d_str = datetime.strptime(d, '%B %d,%Y').strftime('%Y%m%d')
            new_fname = f"ev_turnout_{d_str}.csv"
            print(f"renaming {latest_file} to {new_fname}")
            os.rename(os.path.join(CSV_DL_DIR, latest_file), os.path.join(CSV_DL_DIR, new_fname))

        # don't slam the Sec of State website servers; pause between download loops
        time.sleep(3)
        print("\n")
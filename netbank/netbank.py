#!/usr/bin/python3

from configparser import ConfigParser
from os import devnull, getenv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from time import sleep

# Configure the webdriver and netbank credentials
def prepare_driver(driver_path, download_path, headless):
	# Ensure the config environment variable is set
	auth_path = getenv("AUTH_PATH")
	if auth_path is None:
		print(f"Error - AUTH_PATH environment variable is not set")
		exit(1)

	# Initialise the config parser and ensure netbank information is present
	config = ConfigParser()
	config.read(Path(auth_path))
	if "netbank" not in config:
		print(f"Error - netbank segment not found in config, example template below")
		print("[netbank]\nclient_num:\npassword:")
		exit(1)

	# Set up options for the webdriver
	options = Options()
	if headless == True: options.headless = True

	# If a download path is supplied, set it
	if download_path and download_path.exists():
		options.set_preference("browser.download.folderList", 2)
		options.set_preference("browser.download.dir", download_path)

	# Initialise the firefox driver and log in
	driver = webdriver.Firefox(options=options, service=Service(driver_path, log_path=devnull))
	driver.implicitly_wait(10)

	# Get the login page and send credentials
	username, password = config["netbank"]["client_num"], config["netbank"]["password"]
	driver.get("https://www.my.commbank.com.au/netbank/Logon/Logon.aspx")
	driver.find_element(By.ID, "txtMyClientNumber_field").send_keys(username, Keys.TAB, password, Keys.RETURN)
	return driver


# TODO - Make this work for other accounts
def get_card_trans(driver, acct_index, delay):
	# Navigate to the account
	driver.find_elements(By.CLASS_NAME, "account-link")[acct_index].click()


	# Open advanced menu
	driver.find_element(By.ID, "cba_advanced_search_trigger").click()

	# Navigate the advanced search menu and set it to 120 days
	actions = ActionChains(driver)
	actions.send_keys(Keys.TAB * 3, Keys.ENTER)
	actions.send_keys(Keys.DOWN * 3, Keys.ENTER)
	actions.send_keys(Keys.TAB * 6, Keys.ENTER)
	actions.perform()

	# Open the export menu, set to CSV and download
	driver.find_element(By.ID, "ctl00_CustomFooterContentPlaceHolder_updatePanelExport1").click()
	actions.send_keys(Keys.TAB, Keys.ENTER, Keys.DOWN, Keys.ENTER, Keys.TAB, Keys.ENTER)
	actions.perform()


	# TODO - Load the CSV into memory, delete it, then return it

	return None


driver_path = Path.cwd() / "geckodriver.exe"
download_path = None
driver = prepare_driver(driver_path, download_path, False)
get_card_trans(driver, 1, 1)



sleep(5)
driver.quit()
exit()

# testpath = r"\\wsl$\Ubuntu\tmp"
# TODO
# Set executable for driver as an external variable
# Load and delete CSV file after downloading
# Support for other account types
# Append csv data to existing file


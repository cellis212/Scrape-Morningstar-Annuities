import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException, ElementNotInteractableException

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def save_html_source(driver, filename="login_page_source.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    logging.info(f"Page source saved: {filename}")

def login(driver, username="", password=""):
    url = "https://annuityintel.com/Login.aspx"
    driver.get(url)
    logging.info("Navigating to login page")
    save_html_source(driver)

    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtUsr"))
        )
        username_field.send_keys(username)
        logging.info("Username entered")

        password_field = driver.find_element(By.ID, "txtPwd")
        password_field.send_keys(password)
        logging.info("Password entered")

        login_button = driver.find_element(By.ID, "butLogon")
        login_button.click()
        logging.info("Login button clicked")

        logging.info("Login attempt completed")
        return True

    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Login failed: {str(e)}")
        save_html_source(driver, "login_failed_page_source.html")
        return False

def scrape_data(driver, save_first_html=False):
    all_data = []
    for contract_id in range(17, 7000):  # Loop from 17 to 21 (4 contracts for testing)
        url = f"https://annuityintel.com/MAIProfile/ProfileMain.aspx?ContractIDList={contract_id}"
        driver.get(url)
        logging.info(f"Navigating to contract ID {contract_id}")
        
        # Wait for the page to load
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            logging.error(f"Timeout waiting for page to load for contract ID {contract_id}")
            continue

        # Check for session timeout and re-login if necessary
        if "Your session has timed out" in driver.page_source or driver.current_url == "https://annuityintel.com/SessionTimeout.aspx":
            if not login(driver):
                logging.error(f"Failed to re-login for contract ID {contract_id}. Skipping.")
                continue
            driver.get(url)

        # Save HTML source for the first contract (ID 17)
        if save_first_html and contract_id == 17:
            with open(f"contract_{contract_id}_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logging.info(f"Saved HTML source for contract ID {contract_id}")

        try:
            # Wait for any dynamic content to load
            time.sleep(5)

            # Extract data from the main tab
            main_tab_content = extract_tab_content(driver, "Contract")

            # Click on and extract data from the Benefit tab
            benefit_tab_content = extract_tab_content(driver, "Benefit")

            # Combine all information
            all_content = f"Contract ID: {contract_id}\n\nMain Tab:\n{main_tab_content}\n\n### BENEFIT TAB START ###\n{benefit_tab_content}\n### BENEFIT TAB END ###"

            all_data.append((contract_id, all_content))
            logging.info(f"Scraped contract ID {contract_id}")
            logging.debug(f"Content length: {len(all_content)}")

        except Exception as e:
            logging.error(f"Error processing contract ID {contract_id}: {str(e)}")

    return all_data

def extract_tab_content(driver, tab_name):
    try:
        if tab_name != "Main":
            # Click on the tab
            tab_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{tab_name}')]"))
            )
            tab_element.click()
            logging.info(f"Clicked on {tab_name} tab")

            # Wait for the tab content to load
            time.sleep(3)

        # Get page source and create BeautifulSoup object
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract relevant information from the tab
        tab_content = soup.get_text(separator='\n', strip=True)

        return tab_content

    except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
        logging.error(f"Error extracting content from {tab_name} tab: {str(e)}")
        return f"Error extracting {tab_name} tab content"

def save_to_csv(data, filename="output.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Contract ID", "Page Content"])  # Header
        writer.writerows(data)

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add this line to disable password saving
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    try:
        if login(driver, username="SMUResearch", password="Mstar1"):
            data = scrape_data(driver, save_first_html=True)  # Add save_first_html parameter
            save_to_csv(data, filename="annuity_data.csv")
        else:
            logging.error("Failed to log in. Exiting.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

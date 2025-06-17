import os
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ========== Logging Configuration ==========
# log_dir = r"scraping_logs"
# os.makedirs(log_dir, exist_ok=False)  # Create the directory only

# log_file = os.path.join(log_dir, "scraping_log.txt")  # Now set the full path to the log file
from datetime import datetime

# Create a folder for logs (if it doesn't exist)
log_dir = "scraping_logs"
os.makedirs(log_dir, exist_ok=True)

# Generate a log file name with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(log_dir, f"scraping_log_{timestamp}.txt")

logging.basicConfig(
    filename=log_file,
    filemode='w',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

logging.basicConfig(
    filename=log_file,
    filemode='w',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


# ========== Paths ==========
excel_file = r"input\Input.xlsx"
output_dir = "extracted_articles_from_input_excel"
os.makedirs(output_dir, exist_ok=True)

driver_path = r"edge_driver\msedgedriver.exe"

# ========== Selenium Options ==========
options = Options()
# Uncomment below for headless mode
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")

# ========== Load Excel ==========
try:
    df = pd.read_excel(excel_file)
    logging.info("Excel file '{}' loaded successfully.".format(excel_file))
except Exception as e:
    logging.error("Failed to load Excel file: {}".format(str(e)))
    exit()

# ========== XPaths ==========
TITLE_XPATH = "//h1[@class='entry-title']"
CONTENT_XPATH = "//div[@class='td-post-content tagdiv-type']"

# ========== Web Scraping Logic ==========
try:
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)
    logging.info("WebDriver initialized successfully.\n")

    for _, row in df.iterrows():
        url_id = str(row["URL_ID"]).strip()
        url = str(row["URL"]).strip()
        logging.info("Processing ID: {} | URL: {}".format(url_id, url))

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            title_element = wait.until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))
            content_element = driver.find_element(By.XPATH, CONTENT_XPATH)

            title = title_element.text.strip()
            content = content_element.text.strip()
            
            # Trim Contact details part - 
            # Trim content after 'Contact Details' section (if present)
            
            contact_index = content.lower().find("contact details")
            if contact_index != -1:
                content = content[:contact_index].strip()
                
            full_text = "{}\n\n{}".format(title, content)
            output_path = os.path.join(output_dir, "{}.txt".format(url_id))
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            logging.info("Saved content to '{}'\n".format(output_path))

        except Exception as e:
            logging.warning("Failed to process '{}'\n    Reason: {}\n".format(url, str(e)))

except Exception as e:
    logging.critical("Error initializing Edge WebDriver: {}".format(str(e)))

finally:
    if 'driver' in locals():
        driver.quit()
        logging.info("Browser closed.")

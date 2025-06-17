import os
import pandas as pd
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========== Logging Configuration ==========
log_dir = "scraping_logs"
os.makedirs(log_dir, exist_ok=True)

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

logging.info("Logger initialized.")

# ========== Paths ==========
excel_file = r"input\Input.xlsx"
# output_dir = "extracted_articles_from_input_excel_2"
output_dir = "extracted_articles_from_input_excel_3"
os.makedirs(output_dir, exist_ok=True)

driver_path = r"edge_driver\msedgedriver.exe"

# ========== Selenium Options ==========
options = Options()
# will need to uncomment this for headless mode
# options.add_argument("--headless")

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

        attempt = 0
        success = False

        while attempt < 2 and not success:
            try:
                driver.get(url)
                wait = WebDriverWait(driver, 10)
                # here we are finding on the html DOM with the help of XPATH, which makes the search a lot more accurate and faster than to load whole content inside HTML and then doing it.
                title_element = wait.until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))
                content_element = wait.until(EC.presence_of_element_located((By.XPATH, CONTENT_XPATH)))

                title = title_element.text.strip()
                content = content_element.text.strip()

                # Trim content after 'Contact Details' section, as it is not required as mentioned on the objective.docx
                contact_index = content.lower().find("contact details")
                if contact_index != -1:
                    content = content[:contact_index].strip()

                full_text = "{}\n\n{}".format(title, content)
                output_path = os.path.join(output_dir, "{}.txt".format(url_id))

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(full_text)

                logging.info("Saved content to '{}'\n".format(output_path))
                success = True

            except Exception as e:
                attempt += 1
                if attempt < 2:
                    logging.warning("Attempt {} failed for '{}'. Retrying...\n    Reason: {}".format(attempt, url, str(e)))
                    time.sleep(3)  # Waiting before the retry
                else:
                    logging.error("Failed to process '{}' after 2 attempts.\n    Final Reason: {}\n".format(url, str(e)))

        time.sleep(2)  # Delaying between different URLs

except Exception as e:
    logging.critical("Error initializing Edge WebDriver: {}".format(str(e)))

finally:
    if 'driver' in locals():
        driver.quit()
        logging.info("Browser closed.")

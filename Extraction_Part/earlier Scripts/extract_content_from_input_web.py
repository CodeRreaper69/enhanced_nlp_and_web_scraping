import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# All important Paths - 
# Path to input Excel file
excel_file = r"input\Input.xlsx"
# Path to output Directory where contents will get stored
output_dir = "extracted_articles_from_input_excel"
os.makedirs(output_dir, exist_ok=True)
# path to the driver

# Path to EdgeDriver inside 'edge_driver' folder
# driver_path = os.path.join(os.getcwd(), "edge_driver", "msedgedriver.exe")
driver_path = r"edge_driver\msedgedriver.exe"

# Adding options for providing flags -
# Setup Edge options
options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")

# Load Excel using pandas
try:
    df = pd.read_excel(excel_file)
except Exception as e:
    print(f"Failed to load Excel file: {e}")
    exit()

# Setup XPath expressions
TITLE_XPATH = "//h1[@class='entry-title']"
CONTENT_XPATH = "//div[@class='td-post-content tagdiv-type']"




try:
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    for _, row in df.iterrows():
        url_id = str(row["URL_ID"]).strip()
        url = str(row["URL"]).strip()
        print(f"\nProcessing {url_id} from {url}")

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            title_element = wait.until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))
            content_element = driver.find_element(By.XPATH, CONTENT_XPATH)

            title = title_element.text.strip()
            content = content_element.text.strip()
            
            # Trim content after 'Contact Details' section (if present)
            contact_index = content.lower().find("contact details")
            if contact_index != -1:
                content = content[:contact_index].strip()

            full_text = f"{title}\n\n{content}"
            output_path = os.path.join(output_dir, f"{url_id}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"Saved to {output_path}")

        except Exception as e:
            print(f"Failed to process {url}\n   Reason: {e}")

except Exception as e:
    print(f"Error initializing Edge WebDriver: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
        print("\nBrowser closed.")

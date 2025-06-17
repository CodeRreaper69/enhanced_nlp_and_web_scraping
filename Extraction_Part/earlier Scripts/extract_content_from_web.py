import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# List of article URLs and filenames
articles = [
    {
        "url": "https://insights.blackcoffer.com/efficient-coach-allocation-system-for-sports-coaching-organization/",
        "filename": "Netclan20241045.txt"
    },
    {
        "url": "https://insights.blackcoffer.com/budget-sales-kpi-dashboard-using-power-bi/",
        "filename": "Netclan20241162.txt"
    }
]

# XPath expressions for elements
TITLE_XPATH = "//h1[@class='entry-title']"
CONTENT_XPATH = "//div[@class='td-post-content tagdiv-type']"

# Setup Edge options
options = Options()
# options.add_argument("--headless")  # Uncomment this line to run browser in the background
# options.add_argument("--disable-gpu")  # Optional: sometimes needed for headless mode

# Path to the EdgeDriver inside 'edge_driver' folder
driver_path = os.path.join(os.getcwd(), "edge_driver", "msedgedriver.exe")

# Ensure output folder exists
output_dir = "extracted_articles"
os.makedirs(output_dir, exist_ok=True)

try:
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    for article in articles:
        print("\n📄 Processing", article["filename"], "from", article["url"], "...")
        try:
            driver.get(article["url"])
            wait = WebDriverWait(driver, 10)

            # Wait for the title and content to load
            title_element = wait.until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))
            content_element = driver.find_element(By.XPATH, CONTENT_XPATH)

            title = title_element.text.strip()
            content = content_element.text.strip()

            # Trim content after 'Contact Details' section (if present)
            contact_index = content.lower().find("contact details")
            if contact_index != -1:
                content = content[:contact_index].strip()

            print("✅ Found title and content (", len(content), "characters )")

            # Save to file
            full_text = title + "\n\n" + content
            output_path = os.path.join(output_dir, article["filename"])
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print("💾 Saved to", output_path)

        except Exception as e:
            print("❌ Failed to process", article["url"], "\n   Reason:", str(e))

except Exception as e:
    print("\n🚨 WebDriver Initialization Error:", e)
    print("🔧 Make sure msedgedriver.exe exists in the 'edge_driver' folder")

finally:
    if 'driver' in locals():
        driver.quit()
        print("\n🧹 Browser closed.")
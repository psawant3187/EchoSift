from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def scrape_with_selenium(url):
    options = Options()
    options.add_argument("--headless")  # Run without opening browser
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for JavaScript to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        
        return soup.get_text()  # Extract text content
    except Exception as e:
        driver.quit()
        return f"Error: {e}"

# Example Usage
url = "https://www.airbnb.com/"
content = scrape_with_selenium(url)
print(content[:1000])  # Print a snippet of the scraped content

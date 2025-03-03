from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import io

def init_driver():
    """Initializes and returns a Selenium WebDriver."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("start-maximized")  # Maximize to avoid missing elements
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def scrape_flipkart(search_query):
    """Scrapes product details from Flipkart based on a search query."""
    try:
        url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
        driver = init_driver()
        
        if not driver:
            return [], "WebDriver initialization failed."

        with driver:
            driver.get(url)

            try:
                # Wait for products to load dynamically
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "_1AtVbE"))
                )

                # Get the page source after JavaScript execution
                soup = BeautifulSoup(driver.page_source, "html.parser")
                return parse(soup)

            except Exception as e:
                return [], f"Error occurred while loading page: {str(e)}"
    except Exception as e:
        return [], f"Unexpected error: {str(e)}"

def parse(soup):
    """Parses Flipkart HTML content and extracts product details."""
    try:
        products = []

        for item in soup.find_all('div', {'class': '_1AtVbE'}):
            try:
                product_name = item.find('a', {'class': 'IRpwTa'}) or item.find('a', {'class': 's1Q9rs'})
                price = item.find('div', {'class': '_30jeq3 _1_WHN1'})
                ratings = item.find('div', {'class': '_3LWZlK'})
                availability = item.find('div', {'class': '_2JC05C'})
                description = item.find('ul', {'class': '_1xgFaf'})
                product_link = item.find('a', {'class': '_1fQZEK'})

                if product_name and product_link:
                    products.append({
                        'Product Name': product_name.get_text(strip=True),
                        'Price': price.get_text(strip=True) if price else 'Price not available',
                        'Ratings': ratings.get_text(strip=True) if ratings else 'No ratings available',
                        'Availability': availability.get_text(strip=True) if availability else 'Available',
                        'Description': "\n".join(li.get_text(strip=True) for li in description.find_all('li')) if description else 'No description available',
                        'URL': f"https://www.flipkart.com{product_link['href']}"
                    })
            except Exception as e:
                continue  # Skip items that cause errors
        
        if not products:
            return [], "No products found. Try modifying your search query."
        
        save_to_csv(products)
        return products, None
    except Exception as e:
        return [], f"Parsing error: {str(e)}"

def save_to_csv(products):
    """Saves the scraped product data to a CSV format."""
    try:
        csv_buffer = io.StringIO()
        pd.DataFrame(products).to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    except Exception as e:
        return ""

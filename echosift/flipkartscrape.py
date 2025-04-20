import time
import random
import socket
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def generate_search_query(category, product_name, brand):
    return f"{category} {product_name} {brand}".strip().replace(" ", "+")

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scrape_flipkart(search_query):
    # Determine if it's a full URL or search query
    if search_query.startswith("http"):
        search_url = search_query
    else:
        search_url = f"https://www.flipkart.com/search?q={search_query}"

    driver = init_driver()
    products = []
    total_results = 0

    try:
        driver.get(search_url)
        time.sleep(3)  # Allow page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("div", class_="_1AtVbE")

        for item in items:
            try:
                # Title and URL
                name_tag = item.find("a", {"class": "s1Q9rs"}) or item.find("a", {"class": "IRpwTa"}) or item.find("div", {"class": "_4rR01T"})
                link_tag = item.find("a", {"class": "_1fQZEK"}) or item.find("a", {"class": "s1Q9rs"}) or item.find("a", {"class": "IRpwTa"})

                if not (name_tag and link_tag and link_tag.has_attr("href")):
                    continue

                name = name_tag.get_text(strip=True)
                product_url = f"https://www.flipkart.com{link_tag['href']}"

                # Price
                price_tag = item.find("div", {"class": "_30jeq3 _1_WHN1"}) or item.find("div", {"class": "_30jeq3"})
                price = price_tag.get_text(strip=True) if price_tag else "Price not available"

                # Ratings
                rating_tag = item.find("div", {"class": "_3LWZlK"})
                ratings = rating_tag.get_text(strip=True) if rating_tag else "No ratings available"

                # Image
                image_tag = item.find("img", {"class": "_396cs4"})
                image_url = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

                products.append({
                    "Product Name": name,
                    "Price": price,
                    "Ratings": ratings,
                    "Description": name,  # Use title as description
                    "Product URL": product_url,
                    "Image URL": image_url,
                })
                total_results += 1
            except Exception:
                continue

        metadata = {
            "Search Query": search_query,
            "Search URL": search_url,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Results": total_results,
            "IP Address": socket.gethostbyname("www.flipkart.com"),
        }

        return products, metadata

    except Exception as e:
        return [], {"error": f"Failed to scrape Flipkart: {str(e)}"}

    finally:
        driver.quit()

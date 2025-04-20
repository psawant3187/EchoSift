import requests
from bs4 import BeautifulSoup
import random
import io
import pandas as pd
from datetime import datetime
import socket

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def generate_search_query(category, product_name, brand):
    search_query = f"{category} {product_name} {brand}".strip()
    return search_query.replace(' ', '+')

def scrape_amazon(search_query):
    search_url = f"https://www.amazon.in/s?k={search_query}"
    headers = {"User-Agent": get_random_user_agent()}

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return [], {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    total_results = 0

    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        try:
            product_name = item.h2.get_text(strip=True) if item.h2 else 'No name available'
            price = item.find('span', {'class': 'a-price-whole'})
            price = price.get_text(strip=True) if price else 'Price not available'

            ratings = item.find('span', {'class': 'a-icon-alt'})
            ratings = ratings.get_text(strip=True) if ratings else 'No ratings available'

            # Use product_name as description instead of scraping it
            description = product_name

            product_link = item.find('a', {'class': 'a-link-normal'}, href=True)
            product_url = f"https://www.amazon.in{product_link['href']}" if product_link else 'No URL available'

            image_tag = item.find('img', {'class': 's-image'})
            image_url = image_tag['src'] if image_tag else None

            products.append({
                'Product Name': product_name,
                'Price': price,
                'Ratings': ratings,
                'Description': description,  # <- now same as product name
                'Product URL': product_url,
                'Image URL': image_url
            })
            total_results += 1

        except Exception:
            continue

    metadata = {
        "Search Query": search_query,
        "Search URL": search_url,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Total Results": total_results,
        "Status Code": response.status_code,
        "Content Length": len(response.content),
        "IP Address": socket.gethostbyname("www.amazon.in"),
        "Encoding": response.encoding,
        "Response Headers": str(response.headers),
        "User Agent": headers["User-Agent"],
    }

    return products, metadata

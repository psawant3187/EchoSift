import requests
from bs4 import BeautifulSoup
import random
import io
import pandas as pd
from datetime import datetime

# Random User-Agent for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

def get_random_user_agent():
    try:
        return random.choice(USER_AGENTS)
    except Exception as e:
        return USER_AGENTS[0]  # Default user-agent fallback

# Generate Amazon search query
def generate_search_query(category, product_name, brand):
    try:
        search_query = f"{category} {product_name} {brand}".strip()
        return search_query.replace(' ', '+')
    except Exception as e:
        return ""

# Scrape Amazon products with internal error handling
def scrape_amazon(search_query):
    search_url = f"https://www.amazon.in/s?k={search_query}"
    headers = {"User-Agent": get_random_user_agent()}
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
    except requests.exceptions.HTTPError as e:
        return [], {"error": f"HTTP error: {e}"}
    except requests.exceptions.RequestException as e:
        return [], {"error": f"Network error: {e}"}
    except Exception as e:
        return [], {"error": f"Unexpected error: {e}"}

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        products = []
        total_results = 0

        for item in soup.find_all('div', {'class': 's-result-item'}):
            try:
                product_name = item.h2.get_text(strip=True) if item.h2 else 'No name available'
                price = item.find('span', {'class': 'a-price-whole'})
                price = price.get_text(strip=True) if price else 'Price not available'

                ratings = item.find('span', {'class': 'a-icon-alt'})
                ratings = ratings.get_text(strip=True) if ratings else 'No ratings available'

                availability = item.find('span', {'class': 'a-size-small'})
                availability = availability.get_text(strip=True) if availability else 'Not available'

                description = item.find('span', {'class': 'a-size-base-plus'})
                description = description.get_text(strip=True) if description else 'No description'

                product_link = item.find('a', {'class': 'a-link-normal'})  # Extract product link
                product_url = f"https://www.amazon.in{product_link['href']}" if product_link else 'No URL available'

                products.append({
                    'Product Name': product_name,
                    'Price': price,
                    'Ratings': ratings,
                    'Availability': availability,
                    'Description': description,
                    'Product URL': product_url,
                })
                total_results += 1

            except AttributeError:
                continue  # Skip if any required element is missing
            except Exception as e:
                continue  # Continue processing other elements

        metadata = {
            "search_query": search_query,
            "search_url": search_url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_results": total_results,
        }

        return products, metadata
    except Exception as e:
        return [], {"error": f"Parsing error: {e}"}

# Save products to CSV
def save_to_csv(products):
    try:
        csv_buffer = io.StringIO()
        pd.DataFrame(products).to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    except Exception as e:
        return ""

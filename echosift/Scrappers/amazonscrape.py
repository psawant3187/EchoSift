import random
import socket
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import AMAZON_BASE_URL, USER_AGENTS


def _random_agent() -> str:
    return random.choice(USER_AGENTS)


def generate_search_query(category: str, product_name: str, brand: str) -> str:
    return f"{category} {product_name} {brand}".strip().replace(" ", "+")


def scrape_amazon(search_query: str) -> tuple[list[dict], dict]:
    """
    Scrape Amazon India search results for the given query.

    Returns:
        (products, metadata)
    """
    search_url = f"{AMAZON_BASE_URL}/s?k={search_query}"
    headers = {"User-Agent": _random_agent()}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return [], {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(response.content, "html.parser")
    products: list[dict] = []

    for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
        try:
            name = item.h2.get_text(strip=True) if item.h2 else "No name available"

            price_tag = item.find("span", {"class": "a-price-whole"})
            price = price_tag.get_text(strip=True) if price_tag else "Price not available"

            rating_tag = item.find("span", {"class": "a-icon-alt"})
            ratings = rating_tag.get_text(strip=True) if rating_tag else "No ratings available"

            link_tag = item.find("a", {"class": "a-link-normal"}, href=True)
            product_url = f"{AMAZON_BASE_URL}{link_tag['href']}" if link_tag else "No URL available"

            image_tag = item.find("img", {"class": "s-image"})
            image_url = image_tag["src"] if image_tag else None

            products.append(
                {
                    "Product Name": name,
                    "Price": price,
                    "Ratings": ratings,
                    "Description": name,
                    "Product URL": product_url,
                    "Image URL": image_url,
                }
            )
        except Exception:
            continue

    try:
        ip = socket.gethostbyname("www.amazon.in")
    except Exception:
        ip = "Unavailable"

    metadata = {
        "Search Query": search_query,
        "Search URL": search_url,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Total Results": len(products),
        "Status Code": response.status_code,
        "Content Length": len(response.content),
        "IP Address": ip,
        "Encoding": response.encoding,
        "User Agent": headers["User-Agent"],
    }

    return products, metadata
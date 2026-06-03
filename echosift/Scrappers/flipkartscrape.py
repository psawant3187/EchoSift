import random
import socket
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import FLIPKART_BASE_URL, SCRAPER_PAGE_LOAD_WAIT, USER_AGENTS


def _random_agent() -> str:
    return random.choice(USER_AGENTS)


def _init_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={_random_agent()}")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def generate_search_query(category: str, product_name: str, brand: str) -> str:
    return f"{category} {product_name} {brand}".strip().replace(" ", "+")


def scrape_flipkart(search_query: str) -> tuple[list[dict], dict]:
    """
    Scrape Flipkart search results.

    Args:
        search_query: Either a full Flipkart URL or a search term string.

    Returns:
        (products, metadata)
    """
    search_url = (
        search_query
        if search_query.startswith("http")
        else f"{FLIPKART_BASE_URL}/search?q={search_query}"
    )

    driver = _init_driver()
    products: list[dict] = []

    try:
        driver.get(search_url)
        time.sleep(SCRAPER_PAGE_LOAD_WAIT)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for item in soup.find_all("div", class_="_1AtVbE"):
            try:
                name_tag = (
                    item.find("a", {"class": "s1Q9rs"})
                    or item.find("a", {"class": "IRpwTa"})
                    or item.find("div", {"class": "_4rR01T"})
                )
                link_tag = (
                    item.find("a", {"class": "_1fQZEK"})
                    or item.find("a", {"class": "s1Q9rs"})
                    or item.find("a", {"class": "IRpwTa"})
                )

                if not (name_tag and link_tag and link_tag.has_attr("href")):
                    continue

                name = name_tag.get_text(strip=True)
                product_url = f"{FLIPKART_BASE_URL}{link_tag['href']}"

                price_tag = item.find("div", {"class": "_30jeq3 _1_WHN1"}) or item.find(
                    "div", {"class": "_30jeq3"}
                )
                price = price_tag.get_text(strip=True) if price_tag else "Price not available"

                rating_tag = item.find("div", {"class": "_3LWZlK"})
                ratings = rating_tag.get_text(strip=True) if rating_tag else "No ratings available"

                image_tag = item.find("img", {"class": "_396cs4"})
                image_url = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

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
            ip = socket.gethostbyname("www.flipkart.com")
        except Exception:
            ip = "Unavailable"

        metadata = {
            "Search Query": search_query,
            "Search URL": search_url,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Results": len(products),
            "IP Address": ip,
        }

        return products, metadata

    except Exception as e:
        return [], {"error": f"Failed to scrape Flipkart: {e}"}

    finally:
        driver.quit()
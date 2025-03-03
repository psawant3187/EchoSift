import random
from requests.exceptions import RequestException
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from goose3 import Goose

# Random User-Agent for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
]

def get_random_user_agent():
    try:
        return random.choice(USER_AGENTS)
    except Exception as e:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # Default user-agent

def scrape_website(url):
    headers = {"User-Agent": get_random_user_agent()}
    result = {"title": "", "content": "", "metadata": "", "response_data": "", "images": []}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            g = Goose()
            article = g.extract(raw_html=response.text)
            result["title"] = article.title or "No Title Found"
            result["content"] = article.cleaned_text.strip() or "No content found."
        except Exception as e:
            result["title"] = "Error extracting title"
            result["content"] = "Error extracting content"
        
        try:
            metadata = {
                "Title": result["title"],
                "Description": soup.find("meta", attrs={"name": "description"})["content"]
                if soup.find("meta", attrs={"name": "description"}) else "No Description Found",
            }
            result["metadata"] = metadata
        except Exception as e:
            result["metadata"] = "Error extracting metadata"
        
        result["response_data"] = {
            "Status Code": response.status_code,
            "Content-Type": response.headers.get("Content-Type", "N/A"),
        }
        
        try:
            images = []
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if img_url:
                    images.append(urljoin(url, img_url))
            result["images"] = images
        except Exception as e:
            result["images"] = []
        
        return result
    except RequestException as e:
        return {"error": f"Error retrieving webpage: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

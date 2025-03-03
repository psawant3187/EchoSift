import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

url = "https://www.flipkart.com/laptops+asus"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract Product Title
    title = soup.find("span", {"class": "B_NuCI"}).text if soup.find("span", {"class": "B_NuCI"}) else "N/A"
    
    # Extract Price
    price = soup.find("div", {"class": "_30jeq3 _16Jk6d"}).text if soup.find("div", {"class": "_30jeq3 _16Jk6d"}) else "N/A"

    print(f"Title: {title}\nPrice: {price}")
else:
    print("Failed to retrieve the page")

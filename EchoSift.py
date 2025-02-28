import streamlit as st
import requests
from bs4 import BeautifulSoup
from goose3 import Goose
import pdfplumber
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import random
import io
import pandas as pd
from requests.exceptions import RequestException
from urllib.parse import urljoin
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load model directly
import openai
API_KEY = "ddc-bUOZrLV5gJb4KLXJwnDmaFaS6pd7NcaewGsaaTLV9NWHC7Srmj"
BASE_URL = "https://api.sree.shop/v1"
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Error logging function
def log_error(message):
    print(f"An error occurred: {message}")

# Load Lottie animation
def load_lottie_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        log_error(f"Failed to load Lottie animation: {e}")
        return None

# Random User-Agent for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Scrape Website Content
def scrape_website(url):
    headers = {"User-Agent": get_random_user_agent()}
    result = {"title": "", "content": "", "metadata": "", "response_data": "", "images": []}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        g = Goose()
        article = g.extract(raw_html=response.text)
        result["title"] = article.title or "No Title Found"
        result["content"] = article.cleaned_text.strip() or "No content found."

        metadata = {
            "Title": result["title"],
            "Description": soup.find("meta", attrs={"name": "description"})["content"]
            if soup.find("meta", attrs={"name": "description"}) else "No Description Found",
        }
        result["metadata"] = metadata

        result["response_data"] = {
            "Status Code": response.status_code,
            "Content-Type": response.headers.get("Content-Type", "N/A"),
        }

        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                images.append(urljoin(url, img_url))
        result["images"] = images

        return result
    except RequestException as e:
        return {"error": f"Error retrieving webpage: {e}"}

# Extract text from PDF
def extract_text_from_pdf(file):
    """Extracts text and metadata from a PDF file."""
    try:
        with pdfplumber.open(file) as pdf:
            # Extract text from all pages
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text()).strip()
            
            # Extract metadata from PDF
            metadata = pdf.metadata or {}

            # Return extracted text and metadata dictionary
            return text if text else "No text found in the PDF.", metadata

    except Exception as e:
        return f"Error extracting PDF text: {e}", {}
    
# Summarization function
def summarize_text(text: str) -> str:
    MAX_TOKENS = 4000  # Adjust based on API limits
    try:
        if not text.strip():
            return "No text to summarize."
        
        truncated_text = text[:MAX_TOKENS]  # Limit input size
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Summarize this: {truncated_text}"}]
        )

        return response.choices[0].message.content or "Summary could not be generated."

    except Exception as e:
        return f"Error summarizing text: {e}"


# Save products to CSV
def save_to_csv(products):
    csv_buffer = io.StringIO()
    pd.DataFrame(products).to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# Generate Amazon search query
def generate_search_query(category, product_name, brand):
    search_query = f"{category} {product_name} {brand}".strip()
    return search_query.replace(' ', '+')


# Random User-Agent for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

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

    metadata = {
        "search_query": search_query,
        "search_url": search_url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_results": total_results,
    }

    return products, metadata

# Flipkart Scraper Using Selenium
def scrape_flipkart(search_query):
    def init_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = init_driver()
    driver.get(f"https://www.flipkart.com/search?q={search_query}")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    products = []
    for item in soup.find_all('div', {'class': '_1AtVbE'}):
        try:
            product_name = item.find('a', {'class': 'IRpwTa'}) or item.find('a', {'class': 's1Q9rs'})
            product_name = product_name.get_text(strip=True) if product_name else 'No name available'
            price = item.find('div', {'class': '_30jeq3 _1_WHN1'}).get_text(strip=True) if item.find('div', {'class': '_30jeq3 _1_WHN1'}) else 'Price not available'
            ratings = item.find('div', {'class': '_3LWZlK'}).get_text(strip=True) if item.find('div', {'class': '_3LWZlK'}) else 'No ratings available'
            availability = item.find('div', {'class': '_2JC05C'}).get_text(strip=True) if item.find('div', {'class': '_2JC05C'}) else 'Available'
            description = item.find('ul', {'class': '_1xgFaf'})
            description = "\n".join(li.get_text(strip=True) for li in description.find_all('li')) if description else 'No description available'
            products.append({
                'Product Name': product_name,
                'Price': price,
                'Ratings': ratings,
                'Availability': availability,
                'Description': description,
            })
        except AttributeError:
            continue

    return products, None

# Save products to CSV
def save_to_csv(products):
    csv_buffer = io.StringIO()
    pd.DataFrame(products).to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# Sidebar option menu
with st.sidebar:
    page = option_menu(
        "Main Menu", ["Web Scraping", "PDF Extraction", "Amazon Scraper", "Flipkart Scraper",  "Telegram Bot"],
        icons=["cloud", "file-earmark-pdf", "amazon", "cart","chat-dots"],
        menu_icon="cast", default_index=0,
    )

# Web Scraping Page
if page == "Web Scraping":
    col1, col2 = st.columns([1, 7])
    
    lottie_url = "https://lottie.host/99a68a00-6e33-43fb-9ee6-cccc4c19131d/YcyAardQqk.json"
    lottie_animation = load_lottie_url(lottie_url)

    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
        with col2:
            st.title("Data Extraction from Web")

    st.subheader("Web Scraping Functionality")
    st.write("""
    **Access:** Through the "Web Scraping" option in the sidebar menu.

    **Steps:**
    1. Enter the URL of the website you wish to scrape.
    2. Click "Scrape" to extract content from the webpage.
    3. The content, metadata, and response headers will be displayed.
    4. Optionally, click "Summarize Scraped Content" to generate a summary.
    """)

    url = st.text_input("Enter a URL to scrape")

    if st.button("Scrape Website"):
        if url:
            data = scrape_website(url)
            if "error" in data:
                st.error(data["error"])
            else:
                st.session_state["scraped_content"] = data["content"]
                st.subheader("Title")
                st.write(data["title"])

                st.subheader("Content")
                st.write(data["content"])

                st.subheader("Metadata")
                st.json(data["metadata"])

                st.subheader("Response Data")
                st.json(data["response_data"])

                st.subheader("Images")
                if data["images"]:
                    for img_url in data["images"]:
                        st.image(img_url, caption=img_url, use_container_width=True)
                else:
                    st.write("No images found.")
        else:
            st.error("Please enter a valid URL.")

        if "scraped_content" in st.session_state and st.session_state["scraped_content"]:
            if st.button("Summarize Scraped Content"):
                summary = summarize_text(st.session_state["scraped_content"])
                st.text_area("Summary of Scraped Content", summary, height=150)


# PDF Extraction Page
elif page == "PDF Extraction":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/99a68a00-6e33-43fb-9ee6-cccc4c19131d/YcyAardQqk.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
    with col2:
        st.title("Data Extraction from PDF")

    # Instructions Section
    st.subheader("PDF Text Extraction Functionality")
    st.write("""
    **Access:** Through the "PDF Extraction" option in the sidebar menu.

    **Steps:**
    1. Upload a PDF file.
    2. Click "Extract Text from PDF" to extract the content.
    3. The text will be displayed in the text area.
    4. Optionally, click "Summarize Extracted PDF Text" to summarize the extracted content.
    5. Alternatively, use the "Scrape Website Content" feature to extract web content.
    """)

    # File Upload Section
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Extract text and metadata from the uploaded PDF
        extracted_text, metadata = extract_text_from_pdf(uploaded_file)
        
        # Display Extracted Text
        st.subheader("Extracted Text")
        st.text_area("PDF Content", extracted_text, height=300)

        # Display Metadata (if available)
        if metadata:
            st.subheader("Metadata")
            for key, value in metadata.items():
                st.write(f"**{key}:** {value}")

        # Summarization Section
        if st.button("Summarize Extracted Text"):
            with st.spinner("Generating summary..."):
                summary = summarize_text(extracted_text)
        
            # Display Summary
            st.subheader("Summary of Extracted Text")
            st.text_area("Summary", summary, height=150)
        else:   
            st.warning("No extracted text available for summarization.")

# Amazon Scraper
elif page == "Amazon Scraper":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/99a68a00-6e33-43fb-9ee6-cccc4c19131d/YcyAardQqk.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
    with col2:
        st.title("Amazon Scraper")
    
    # Instructions
    st.subheader("Instructions")
    st.markdown("""
    **Steps to use Amazon Scraper:**
    1. Enter the category of the product you want to search.
    2. Optionally, provide a product name or brand for more specific results.
    3. Click "Scrape Amazon" to retrieve product details.
    4. The results will be displayed in a table, and you can download them as a CSV file.
    """)

    # User Input Fields
    category = st.text_input("Enter the category (required)", "").strip()
    product_name = st.text_input("Enter the product name (optional)", "").strip()
    brand = st.text_input("Enter the brand (optional)", "").strip()

    # Button for Scraping
    if st.button("Scrape Amazon"):
        if category:
            search_query = generate_search_query(category, product_name, brand)
            with st.spinner("Fetching Amazon products..."):
                products = []
                metadata = {}

                # Retry logic (Up to 3 attempts)
                for attempt in range(3):
                    products, metadata = scrape_amazon(search_query)
                    if products:
                        break  # Exit loop if successful

                # Error Handling
                if "error" in metadata:
                    st.error(f"Error: {metadata['error']}. Please try again later.")
                elif products:
                    # Display Metadata
                    st.subheader("Search Metadata")
                    st.json(metadata)  # Show metadata as structured JSON
                    
                    # Display Results
                    df = pd.DataFrame(products)
                    st.subheader("Scraped Results")
                    st.dataframe(df)

                    # Convert DataFrame to CSV
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download as CSV",
                        data=csv_data,
                        file_name=f"amazon_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No products found. Try a different search query.")
        else:
            st.error("Please enter a product category.")

# Flipkart Scraper Page
elif page == "Flipkart Scraper":
    # Layout: Lottie animation on the left and title on the right
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/8ef544f8-2f05-4f15-90a9-64652158ae6a/BSZPC5XVB5.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="flipkart_lottie")
    with col2:
        st.title("Flipkart Scraper")

    # Instructions
    st.subheader("Instructions")
    st.write("""
    **Steps to use Flipkart Scraper:**
    1. Enter the product category you want to search.
    2. Optionally, provide a product name or brand for more specific results.
    3. Click "Scrape Flipkart" to retrieve product details.
    4. The results will display in a table, and you can download them as a CSV file.
    """)

    # Input Fields
    category = st.text_input("Enter the category (required)", "")
    product_name = st.text_input("Enter the product name (optional)", "")
    brand = st.text_input("Enter the brand (optional)", "")

    # Scrape Button
    if st.button("Scrape Flipkart"):
        if category:
            search_query = generate_search_query(category, product_name, brand)
            products, error = scrape_flipkart(search_query)

            if error:
                st.error(error)
            elif products:
                # Display results and provide CSV download
                csv_data = save_to_csv(products)
                st.dataframe(pd.DataFrame(products))
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="flipkart_products.csv",
                    mime="text/csv"
                )
            else:
                st.error("No products found. Try a different search query.")
        else:
            st.error("Please enter a product category.")

# Telegram Bot Page
elif page == "Telegram Bot":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/99a68a00-6e33-43fb-9ee6-cccc4c19131d/YcyAardQqk.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
    with col2:
        st.title("Telegram Bot")

    st.subheader("Telegram Bot Integration")
    st.write(""" 
    **Steps:**
    1. Use the EchoSift Telegram bot to interact with data extraction.
    2. Send URLs or PDFs to the bot and receive extracted or summarized content.
    """)
    st.write("Link: [EchoSift Telegram Bot](https://t.me/EchoSiftBot)")

import streamlit as st
import requests
from bs4 import BeautifulSoup
from goose3 import Goose
import pdfplumber
from summa import summarizer
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import nltk
import random
import io
import pandas as pd
from requests.exceptions import RequestException

# Download required NLTK data files
nltk.download('punkt')

# Custom CSS for background image
background_image_url = "https://i.ibb.co/L0mQ3Fs/Background-Image.jpg"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({background_image_url});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Load Lottie animation
def load_lottie_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Failed to load Lottie animation: {e}")
        return None

# Random User-Agent for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Scrape Website Content
def scrape_website(url: str) -> str:
    headers = {"User-Agent": get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        g = Goose()
        article = g.extract(url=url)

        title = article.title or "No Title Found"
        body = article.cleaned_text.strip() or "No content found."

        if not body:
            paragraphs = soup.find_all("p")
            body = "\n\n".join(p.text for p in paragraphs if p.text)

        return f"Title: {title}\n\nContent:\n{body or 'No text found on the page.'}"

    except RequestException as req_err:
        return f"Network error: {req_err}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Extract text from PDF
def extract_text_from_pdf(file) -> str:
    try:
        with pdfplumber.open(file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
            return text.strip() or "No text found in the PDF."
    except Exception as e:
        return f"Error extracting PDF text: {e}"

# Summarize text using Summa TextRank
def summarize_text(text: str) -> str:
    if not text.strip():
        return "No text to summarize."
    summary = summarizer.summarize(text)
    return summary if summary else "Summary could not be generated."

# Save products to CSV
def save_to_csv(products):
    csv_buffer = io.StringIO()
    pd.DataFrame(products).to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# Generate Amazon search query
def generate_search_query(category, product_name, brand):
    search_query = f"{category} {product_name} {brand}".strip()
    return search_query.replace(' ', '+')

# Scrape Amazon products
def scrape_amazon(search_query):
    search_url = f"https://www.amazon.in/s?k={search_query}"
    headers = {"User-Agent": get_random_user_agent()}
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except RequestException as e:
        return [], f"Network error occurred: {e}"
    
    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    
    for item in soup.find_all('div', {'class': 's-result-item'}):
        try:
            product_name = item.h2.get_text(strip=True) if item.h2 else 'No name available'
            price = item.find('span', {'class': 'a-price-whole'}).get_text(strip=True) if item.find('span', {'class': 'a-price-whole'}) else 'Price not available'
            ratings = item.find('span', {'class': 'a-icon-alt'}).get_text(strip=True) if item.find('span', {'class': 'a-icon-alt'}) else 'No ratings available'
            availability = item.find('span', {'class': 'a-size-small'}).get_text(strip=True) if item.find('span', {'class': 'a-size-small'}) else 'Not available'
            description = item.find('span', {'class': 'a-size-base-plus'}).get_text(strip=True) if item.find('span', {'class': 'a-size-base-plus'}) else 'No description'
            
            products.append({
                'Product Name': product_name,
                'Price': price,
                'Ratings': ratings,
                'Availability': availability,
                'Description': description
            })
        except AttributeError:
            continue
    
    return products, None

# Sidebar option menu
with st.sidebar:
    page = option_menu(
        "Main Menu", ["Web Scraping", "PDF Extraction", "Amazon Scraper", "Telegram Bot"],
        icons=["cloud", "file-earmark-pdf", "amazon", "chat-dots"],
        menu_icon="cast", default_index=0,
    )

# Web Scraping Page
if page == "Web Scraping":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/33d5d406-f666-4359-8702-3847dcef4b58/JkXh2nRM6v.json"
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
    3. The content will be displayed in the text area.
    4. Optionally, click "Summarize Scraped Content" to summarize the text.
    """)

    url = st.text_input("Enter a URL to scrape")
    if st.button("Scrape"):
        if url:
            scraped_content = scrape_website(url)
            st.session_state['scraped_content'] = scraped_content
            st.text_area("Scraped Content", scraped_content, height=300)
        else:
            st.error("Please enter a valid URL.")

    if 'scraped_content' in st.session_state and st.button("Summarize Scraped Content"):
        summary = summarize_text(st.session_state['scraped_content'])
        st.text_area("Summary of Scraped Content", summary, height=150)

# PDF Extraction Page
elif page == "PDF Extraction":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/33d5d406-f666-4359-8702-3847dcef4b58/JkXh2nRM6v.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
    with col2:
        st.title("Data Extraction from PDF")

    st.subheader("PDF Text Extraction Functionality")
    st.write(""" 
    **Access:** Through the "PDF Extraction" option in the sidebar menu.

    **Steps:**
    1. Upload a PDF file.
    2. Click "Extract Text from PDF" to extract the content.
    3. The text will be displayed in the text area.
    4. Optionally, click "Summarize Extracted PDF Text" to summarize the extracted content.
    """)

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if st.button("Extract Text from PDF"):
        if uploaded_file:
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.session_state['pdf_text'] = pdf_text
            st.text_area("Extracted PDF Text", pdf_text, height=300)
        else:
            st.error("Please upload a PDF file.")

    if 'pdf_text' in st.session_state and st.button("Summarize Extracted PDF Text"):
        summary = summarize_text(st.session_state['pdf_text'])
        st.text_area("Summary of Extracted PDF Text", summary, height=150)

# Amazon Scraper Page
elif page == "Amazon Scraper":
    st.title("Amazon Product Scraper")
    
    st.subheader("Instructions")
    st.write(""" 
    **Steps to use Amazon Scraper:**
    1. Enter the category of the product you want to search.
    2. Optionally, provide a product name or brand for more specific results.
    3. Click "Scrape Amazon" to retrieve product details.
    4. The results will display in a table, and you can download them as a CSV file.
    """)

    category = st.text_input("Enter the category (required)", "")
    product_name = st.text_input("Enter the product name (optional)", "")
    brand = st.text_input("Enter the brand (optional)", "")
    
    if st.button("Scrape Amazon"):
        if category:
            search_query = generate_search_query(category, product_name, brand)
            products, error = scrape_amazon(search_query)
            
            if error:
                st.error(error)
            elif products:
                csv_data = save_to_csv(products)
                st.dataframe(pd.DataFrame(products))
                st.download_button("Download as CSV", data=csv_data, file_name="amazon_products.csv", mime="text/csv")
            else:
                st.error("No products found. Try a different search query.")
        else:
            st.error("Please enter a product category.")

# Telegram Bot Page
elif page == "Telegram Bot":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/33d5d406-f666-4359-8702-3847dcef4b58/JkXh2nRM6v.json"
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
    st.write("Link: [EchoSift Telegram Bot](https://t.me/EchoSift)")

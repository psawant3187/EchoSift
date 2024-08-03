# main.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from goose3 import Goose
import pdfplumber
from streamlit_lottie import st_lottie  # Import the streamlit-lottie library


def scrape_website(url: str) -> str:
    """Scrapes a website and returns the title and text of the page."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        g = Goose()
        article = g.extract(url=url)

        title = article.title or "No Title Found"
        body = article.cleaned_text

        if not body:
            paragraphs = soup.find_all("p")
            body = "\n\n".join(p.text for p in paragraphs if p.text)

        if not body:
            body = "No text found on the page."

        return f"Title: {title}\n\nContent:\n{body}"

    except requests.exceptions.RequestException as req_err:
        return f"Network error: {req_err}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def extract_text_from_pdf(file) -> str:
    """Extracts text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip() if text.strip() else "No text found in the PDF."
    except Exception as e:
        return f"Sorry, I couldn't extract text from this PDF. Error: {e}"

def load_lottie_url(url: str):
    """Loads a Lottie animation from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Lottie animation from {url}")
        return None
    
# Load and display the Lottie animation
lottie_url = "https://lottie.host/20b8c958-ba15-48ff-8623-24441a725eb0/mCJ86ypilt.json"
lottie_animation = load_lottie_url(lottie_url)

# Streamlit UI
st.title("EchoSift - Web Scraper and PDF Extractor")

if lottie_animation:
    st_lottie(lottie_animation,speed=1,reverse=False,loop=True,quality="high",height=300,width=300,key="scraper_animation",)

# Web Scraping Section
st.header("Web Scraping")
url = st.text_input("Enter a URL to scrape")
if st.button("Scrape"):
    if url:
        scraped_content = scrape_website(url)
        st.text_area("Scraped Content", scraped_content, height=300)
    else:
        st.error("Please enter a valid URL")

# PDF Extraction Section
st.header("PDF Text Extraction")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if st.button("Extract Text from PDF"):
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted PDF Text", pdf_text, height=300)
    else:
        st.error("Please upload a PDF file")

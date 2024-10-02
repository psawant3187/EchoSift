import streamlit as st
import requests
from bs4 import BeautifulSoup
from goose3 import Goose
import pdfplumber
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import nltk

# Download required NLTK data files
nltk.download('punkt')

# Custom CSS for background image
background_image_url = "https://i.ibb.co/L0mQ3Fs/Background-Image.jpg"  # Replace with your image URL
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

# Helper functions for data extraction
def scrape_website(url: str) -> str:
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
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Lottie animation from {url}")
        return None

def summarize_text(text: str, sentence_count: int = 5) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

# Sidebar option menu with separate pages
with st.sidebar:
    page = option_menu(
        "Main Menu", ["Web Scraping", "PDF Extraction", "Telegram Bot"],
        icons=["cloud", "file-earmark-pdf", "chat-dots"],
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
        st.title("Data Extraction from WEB")
    # Instructions
    st.subheader("Web Scraping Functionality")
    st.write("""
    **Access:** Through the "Web Scraping" option in the sidebar menu.

    **Steps:**
    1. On the "Web Scraping" page, enter the URL of the website you wish to scrape in the text input field.
    2. Click the "Scrape" button to start the web scraping process.
    3. The content extracted from the webpage will be displayed in the "Scraped Content" text area.
    4. If desired, click the "Summarize Scraped Content" button to summarize the extracted content. The summary will be displayed in a new text area.

    **Function:**
    - Uses requests and BeautifulSoup to scrape website content.
    - Goose3 library is used for extracting article titles and text, with a fallback to manual scraping of paragraphs if necessary.
    """)

    # Web Scraping Section
    st.header("Web Scraping")
    url = st.text_input("Enter a URL to scrape")
    if st.button("Scrape"):
        if url:
            scraped_content = scrape_website(url)
            st.session_state['scraped_content'] = scraped_content
            st.text_area("Scraped Content", scraped_content, height=300)
        else:
            st.error("Please enter a valid URL")

    # Summarization Section for Scraped Content
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

    # Instructions
    st.subheader("PDF Text Extraction Functionality")
    st.write("""
    **Access:** Through the "PDF Extraction" option in the sidebar menu.

    **Steps:**
    1. On the "PDF Text Extraction" page, upload a PDF file using the "Upload a PDF file" option.
    2. Click the "Extract Text from PDF" button to extract the text from the PDF.
    3. The extracted text will be displayed in the "Extracted PDF Text" text area.
    4. If desired, click the "Summarize Extracted PDF Text" button to summarize the extracted content.

    **Function:**
    - Uses pdfplumber to extract text from each page of the uploaded PDF.
    - Provides a summary using the sumy library with LSA summarization (Latent Semantic Analysis).
    """)

    # PDF Extraction Section
    st.header("PDF Text Extraction")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if st.button("Extract Text from PDF"):
        if uploaded_file:
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.session_state['pdf_text'] = pdf_text
            st.text_area("Extracted PDF Text", pdf_text, height=300)
        else:
            st.error("Please upload a PDF file")

    # Summarization Section for Extracted PDF Text
    if 'pdf_text' in st.session_state and st.button("Summarize Extracted PDF Text"):
        summary = summarize_text(st.session_state['pdf_text'])
        st.text_area("Summary of Extracted PDF Text", summary, height=150)

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

    # Instructions
    st.subheader("Telegram Bot Integration")
    st.write("""
    **Access:** Through the "Telegram Bot" option in the sidebar menu.

    **Steps:**
    1. On the "Telegram Bot" page, follow the link to the EchoSift Telegram bot.
    2. The bot allows you to send URLs or PDF files directly via Telegram.
    3. It will return extracted or summarized content based on the input.

    **Function:**
    - Provides a Telegram interface where users can interact with the bot to perform the same data extraction tasks.
    - The bot link is provided on the page for easy access.
    """)

    st.write("""
        Our Telegram bot provides the same data extraction capabilities directly within Telegram. 
        Send URLs or PDF files to the bot, and it will extract the text for you.
    """)
    st.write("Link: [EchoSift Telegram Bot](https://t.me/EchoSift)")

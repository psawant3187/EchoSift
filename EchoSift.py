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

# Summarization function using sumy (LSA summarization)
def summarize_text(text: str, sentence_count: int = 5) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

# Sidebar option menu
with st.sidebar:
    page = option_menu(
        "Main Menu", ["Home", "Data Extraction", "About Us", "Contact Us", "Telegram Bot"],
        icons=["house", "tools", "info-circle", "envelope", "chat-dots"],
        menu_icon="cast", default_index=0,
    )

# Home Page
if page == "Home":
    col1, col2 = st.columns([1, 7])
    lottie_url = "https://lottie.host/33d5d406-f666-4359-8702-3847dcef4b58/JkXh2nRM6v.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        with col1:
            st_lottie(lottie_animation, speed=1, height=100, key="home_lottie")
    with col2:
        st.title("Welcome to EchoSift!")
    st.header("This is the home page of the EchoSift app, a powerful tool for web scraping and PDF text extraction.")
    gif_url = "EchoSift.gif"  # Replace with your GIF URL or file path
    st.image(gif_url, use_column_width=True)
    st.write("This project proposes a novel approach that integrates web scraping with secure data transfer using blockchain technology. A scrapper will extract data as usual, but instead of direct transfer, the information will be stored and shared securely on an immutable blockchain ledger. This approach aims to:")
    st.write("•	Enhance data security: By leveraging blockchain's secure infrastructure, the project aims to minimize the risk of data breaches during transfer.")
    st.write("•	Potentially improve response rates: The project investigates whether the reduced load on target websites due to blockchain storage might lead to a higher probability of receiving successful responses (200 code).")
    st.write("The project will explore the implementation details, analyze its effectiveness in achieving the stated goals, and discuss the potential implications and future directions for this secure and efficient data extraction method.")
    st.header("Key Benefits")
    st.write("Enhancing Data Security: The core advantage of our approach lies in its ability to enhance data security. Blockchain technology offers an immutable and decentralized ledger that is highly resistant to tampering. By leveraging this secure infrastructure, we significantly minimize the risk of data breaches during the transfer process. The immutable nature of blockchain ensures that once the data is stored, it cannot be altered or deleted, providing an unprecedented level of security and trust.")
    st.write("Improving Response Rates: Another critical aspect of our project is the potential to improve response rates from target websites. Traditional web scraping methods often place a significant load on websites, leading to failed requests or slow responses. By offloading the storage and transfer of data to a blockchain, we hypothesize that the reduced strain on target websites might lead to a higher probability of receiving successful responses, such as the HTTP 200 status code. This aspect of our project is currently under investigation, and we are excited about the possibilities it holds for more efficient data extraction.")

# Data Extraction Page
elif page == "Data Extraction":
    st.title("Data Extraction")
    
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

    if 'scraped_content' in st.session_state and st.button("Summarize Scraped Content"):
        summary = summarize_text(st.session_state['scraped_content'])
        st.text_area("Summary of Scraped Content", summary, height=150)

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

    if 'pdf_text' in st.session_state and st.button("Summarize Extracted PDF Text"):
        summary = summarize_text(st.session_state['pdf_text'])
        st.text_area("Summary of Extracted PDF Text", summary, height=150)

# About Us Page
elif page == "About Us":
    st.title("About Us")
    st.write("At the forefront of innovation, our project is dedicated to redefining how data is extracted, transferred, and secured on the web. In an era where data breaches and security threats are increasingly common, our team recognized the urgent need for a more robust and reliable system. Thus, we propose a novel approach that seamlessly integrates web scraping with secure data transfer using blockchain technology.")
    st.write("Web scraping has long been a valuable tool for gathering information from the vast expanses of the internet. However, the traditional methods of data transfer have exposed vulnerabilities that can lead to significant security risks. Our project addresses this critical issue by introducing an innovative solution that not only extracts data but also ensures its secure transfer through an immutable blockchain ledger.")
    st.header("Our Approach")
    st.write("Our approach begins with a traditional web scraper that extracts data from target websites. However, instead of transferring this data directly, we utilize the decentralized and secure infrastructure of blockchain technology. By storing the scraped information on a blockchain, we ensure that the data remains secure, unaltered, and traceable throughout its lifecycle.")
    st.header("Our Team")
    st.write("Our team is a dynamic group of innovators, engineers, and data enthusiasts, united by a shared passion for pushing the boundaries of technology. With a deep understanding of web scraping, data security, and blockchain technology, we bring together a diverse range of expertise to tackle the complex challenges of modern data transfer.")
    st.write("Each member of our team contributes a unique perspective, combining technical prowess with a forward-thinking mindset. Our engineers are skilled in the intricacies of web scraping and blockchain integration, ensuring that our solutions are both cutting-edge and practical. Meanwhile, our data security experts focus on safeguarding information, ensuring that every step of our process meets the highest standards of protection.")
    st.write("Together, we are dedicated to creating a secure and efficient future for data extraction and transfer. Our collective expertise and unwavering commitment to innovation drive us forward, as we work to transform the way data is handled in the digital age.")
    st.header("Join Us on Our Journey")
    st.write("We invite you to join us on this exciting journey as we work towards a more secure and efficient future for data extraction. Whether you are a fellow innovator, a potential collaborator, or simply someone interested in the future of technology, we welcome your interest and engagement.")

# Contact Us Page
elif page == "Contact Us":
    st.title("Contact Us")
    st.write("""
        We'd love to hear from you! Whether you have a question about features, 
        pricing, need a demo, or anything else, our team is ready to assist.
    """)
    st.write("Email: support@echosift.com")
    st.write("Phone: +123-456-7890")

# Telegram Bot Page
elif page == "Telegram Bot":
    st.title("Telegram Bot")
    st.write("""
        Our Telegram bot provides the same data extraction capabilities directly within Telegram. 
        Send URLs or PDF files to the bot, and it will extract the text for you.
    """)
    st.write("Link: [EchoSift Telegram Bot](https://t.me/EchoSift)")

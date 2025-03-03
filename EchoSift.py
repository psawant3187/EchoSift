import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
from echosift.websitescrape import *
from echosift.pdfextract import *
from echosift.summarization import *
from echosift.amazonscrape import *
from echosift.flipkartscrape import *

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
            st_lottie(lottie_animation, speed=1, height=100, key="web_scraping_anim")
        with col2:
            st.title("Data Extraction from Web")

    st.subheader("Web Scraping Functionality")
    st.write("""
    **Access:** Through the "Web Scraping" option in the sidebar menu.

    **Steps:**
    1. Enter the URL of the website you wish to scrape.
    2. Click "Scrape Website" to extract content from the webpage.
    3. View extracted content, metadata, and response headers.
    4. Optionally, click "Summarize Scraped Content" to generate a summary.
    """)

    url = st.text_input("Enter a URL to scrape", placeholder="https://example.com")

    if st.button("Scrape Website"):
        if url.strip():
            with st.spinner("Scraping website..."):
                data = scrape_website(url)
            if "error" in data:
                st.error(data["error"])
            else:
                st.session_state["scraped_content"] = data["content"]
                st.session_state["scraped_title"] = data["title"]

                st.subheader("Title")
                st.write(data["title"] if data["title"] else "No Title Found")

                st.subheader("Content")
                st.write(data["content"] if data["content"] else "No Content Found")

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
            with st.spinner("Generating Summary..."):
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
    1. **Option 1:** Enter the **category, product name, or brand** to search automatically.  
    2. **Option 2:** Enter a **specific Flipkart URL** to scrape a custom page.  
    3. Click "Scrape Flipkart" to retrieve product details.  
    4. The results will display in a table, and you can download them as a CSV file.  
    """)

    # Input Fields
    flipkart_url = st.text_input("Enter Flipkart URL (optional)", "")
    category = st.text_input("Enter the category (optional)", "")
    product_name = st.text_input("Enter the product name (optional)", "")
    brand = st.text_input("Enter the brand (optional)", "")

    # Scrape Button
    if st.button("Scrape Flipkart"):
        if flipkart_url:
            search_query = flipkart_url  # Use the URL directly
        elif category:
            search_query = generate_search_query(category, product_name, brand)  # Use generated query
        else:
            st.error("Please enter a category or Flipkart URL.")
            st.stop()

        products, error = scrape_flipkart(search_query)

        if error:
            st.error(error)
        else:
            df = pd.DataFrame(products)
            if not df.empty:
                st.dataframe(df)
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="flipkart_products.csv",
                    mime="text/csv"
                )
            else:
                st.error("No products found. Try a different search query.")

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

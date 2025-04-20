import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
from echosift.websitescrape import *
from echosift.pdfextract import *
from echosift.modelfunctions import *
from echosift.amazonscrape import *
from echosift.flipkartscrape import *
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from requests.exceptions import RequestException

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

st.set_page_config(layout="wide")

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
    **Steps:**
    1. Enter the URL of the website you wish to scrape.
    2. Set the maximum depth of pages to scrape.
    3. Click "Scrape Website" to extract content from the webpage.
    4. View extracted content, metadata, response headers, and images.
    5. Optionally summarize and ask questions about the scraped content.
    """)

    # Reset Button
    if st.button("🔄 Reset All"):
        st.session_state.pop('pdf_text', None)
        st.session_state.pop('pdf_summary', None)
        st.session_state.pop('pdf_qa_history', None)
        st.rerun()

    url = st.text_input("Enter a URL to scrape", placeholder="https://example.com")
    max_depth = st.slider("Select the scraping depth", min_value=1, max_value=5, value=2)

    col_scrape_btn, col_summary_btn, col_reset_btn = st.columns(3)

    with col_scrape_btn:
        if st.button("Scrape Website"):
            if url.strip():
                with st.spinner("Scraping website..."):
                    results = scrape_website(url, max_depth=max_depth)
                if results:
                    st.session_state["scraped_results"] = results
                    st.session_state["scraped_content"] = "\n\n".join(r.get("content", "") for r in results)
                    st.session_state["scraped_title"] = results[0].get("title", "")
                    st.session_state["scraped_summary"] = ""
                else:
                    st.session_state["scraped_results"] = None
                    st.error("No data found or an error occurred.")
            else:
                st.error("Please enter a valid URL.")

    with col_summary_btn:
        if st.button("Summarize Scraped Content") and st.session_state.get("scraped_content"):
            with st.spinner("Generating Summary..."):
                summary = summarize_website_text(st.session_state["scraped_content"])
                st.session_state["scraped_summary"] = summary

    with col_reset_btn:
        if st.button("Reset All"):
            for key in ["scraped_results", "scraped_content", "scraped_title", "scraped_summary"]:
                st.session_state.pop(key, None)
            st.experimental_rerun()

    if st.session_state.get("scraped_results"):
        all_results = st.session_state["scraped_results"]
        titles = [res.get("title", f"Page {i+1}") for i, res in enumerate(all_results)]

        st.subheader("🔍 Filter Scraped Content")
        selected_title = st.selectbox("Filter by Page Title (Optional)", ["All Pages"] + titles)
        keyword_filter = st.text_input("Filter by Keyword in Content (Optional)", "")

        def apply_filters(results):
            filtered = []
            for i, res in enumerate(results):
                title = res.get("title", f"Page {i+1}")
                content = res.get("content", "")
                if selected_title != "All Pages" and title != selected_title:
                    continue
                if keyword_filter and keyword_filter.lower() not in content.lower():
                    continue
                filtered.append(res)
            return filtered

        filtered_results = apply_filters(all_results)

        col_scraped_data, col_summary_output = st.columns(2)

        with col_scraped_data:
            st.subheader("📝 Extracted Content")
            combined_content = "\n\n".join(result.get("content", "") for result in filtered_results)
            st.write(combined_content or "No Content Found.")

            st.subheader("🧾 Metadata & Response Details")
            with st.expander("View Combined Metadata & Response Info", expanded=False):
                for i, result in enumerate(filtered_results, 1):
                    st.markdown(f"### Page {i}: {result.get('title', 'No Title')}")
                    combined_info = {
                        **result.get("metadata", {}),
                        **result.get("response_data", {})
                    }
                    st.json(combined_info)

            st.subheader("🖼️ Extracted Images")
            any_images = False
            for result in filtered_results:
                for img_url in result.get("images", []):
                    try:
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            img = Image.open(BytesIO(response.content))
                            st.image(img, caption=img_url, use_container_width=True)
                            any_images = True
                    except Exception:
                        continue
            if not any_images:
                st.write("No images found.")

        with col_summary_output:
            st.subheader("🧠 Summary of Scraped Content")
            if st.session_state.get("scraped_summary"):
                st.markdown(f"""
                    <div style="padding: 1rem; background-color: #1c1c1e; border-radius: 10px; color: white;">
                        {st.session_state['scraped_summary']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No summary generated yet.")

            st.markdown("---")
            st.subheader("💬 Ask Questions about Scraped Content")
            user_question = st.text_input("Enter your question", placeholder="e.g., What is the main service provided by the site?")

            if st.button("Ask") and user_question.strip():
                with st.spinner("Thinking..."):
                    content_to_use = st.session_state.get("scraped_content", "")[:4000]
                    answer = ask_website_question(content_to_use, user_question)
                    st.markdown(f"""
                        <div style="padding: 1rem; background-color: #2c2c2e; border-radius: 10px; color: white;">
                            {answer}
                        </div>
                    """, unsafe_allow_html=True)

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

    st.subheader("📌 Instructions")
    st.markdown("""
    1. Upload a PDF file.
    2. Click **Extract Text from PDF** to extract the content.
    3. Click **Summarize** to summarize the extracted text.
    4. Ask questions to get answers from the content.
    5. Use **Reset All** to clear everything.
    """)

    # Reset Button
    if st.button("🔄 Reset All"):
        st.session_state.pop('pdf_text', None)
        st.session_state.pop('pdf_summary', None)
        st.session_state.pop('pdf_qa_history', None)
        st.rerun()

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        extracted_text, metadata = extract_text_from_pdf(uploaded_file)
        st.session_state.pdf_text = extracted_text
        st.session_state.pdf_metadata = metadata

    if 'pdf_text' in st.session_state:
        # Two-column layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Extracted Data")
            st.markdown(f"""
                <div style="padding: 1rem; background-color: #1c1c1e; border-radius: 10px; color: white; overflow:auto; max-height: 400px;">
                    {st.session_state['pdf_text'].replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("📊 Metadata")
            with st.expander("Click to view metadata"):
                for k, v in st.session_state.get('pdf_metadata', {}).items():
                    st.write(f"**{k}:** {v}")

        # Summary section
        if st.button("📝 Summarize Extracted Text"):
            with st.spinner("Generating summary..."):
                summary = summarize_pdf_text(st.session_state['pdf_text'])
                st.session_state.pdf_summary = summary

        if 'pdf_summary' in st.session_state:
            st.subheader("📚 Summary")
            st.markdown(f"""
                <div style="padding: 1rem; background-color: #1c1c1e; border-radius: 10px; color: white;">
                    {st.session_state['pdf_summary'].replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

        # QnA Section
        st.subheader("💬 Ask Questions About the PDF")
        if 'pdf_qa_history' not in st.session_state:
            st.session_state.pdf_qa_history = []

        user_question = st.text_input("Type your question here:")

        if st.button("Ask"):
            if user_question:
                with st.spinner("Thinking..."):
                    answer = ask_pdf_question(st.session_state['pdf_text'], user_question)
                    st.session_state.pdf_qa_history.append({"q": user_question, "a": answer})
            else:
                st.warning("Please enter a valid question.")

        if st.session_state.pdf_qa_history:
            for idx, qa in enumerate(reversed(st.session_state.pdf_qa_history), 1):
                st.markdown(f"""
                    <div style="margin-bottom: 1rem; padding: 1rem; border-radius: 8px; background-color: #262730;">
                        <b style="color: #58a6ff;">Q{idx}:</b> {qa['q']}<br><br>
                        <b style="color: #a8ff60;">A:</b> {qa['a']}
                    </div>
                """, unsafe_allow_html=True)

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

    st.subheader("📌 Instructions")
    st.markdown("""
    1. Enter the product category you want to search.
    2. Optionally, add a product name or brand.
    3. Click **Scrape Amazon** to get product details.
    4. Compare selected products side by side.
    """)

    if "products" not in st.session_state:
        st.session_state.products = []
    if "metadata" not in st.session_state:
        st.session_state.metadata = {}

    category = st.text_input("Enter the category (required)", "").strip()
    product_name = st.text_input("Enter the product name (optional)", "").strip()
    brand = st.text_input("Enter the brand (optional)", "").strip()

    col_scrape, col_reset = st.columns([2, 1])
    with col_scrape:
        scrape_btn = st.button("Scrape Amazon")
    with col_reset:
        reset_btn = st.button("🔄 Reset")

    if scrape_btn:
        if category:
            search_query = generate_search_query(category, product_name, brand)
            with st.spinner("🔍 Fetching products from Amazon..."):
                products, metadata = scrape_amazon(search_query)

            if "error" in metadata:
                st.error(f"❌ Error: {metadata['error']}")
            elif products:
                st.success("✅ Products scraped successfully!")
                st.session_state.products = products
                st.session_state.metadata = metadata
            else:
                st.warning("⚠️ No products found. Try a different search query.")
        else:
            st.error("🚫 Please enter a product category.")

    if reset_btn:
        st.session_state.products = []
        st.session_state.metadata = {}
        st.rerun()

    if st.session_state.products:
        products = st.session_state.products
        metadata = st.session_state.metadata

        st.subheader("📊 Sort Products")
        sort_option = st.selectbox(
            "Select sorting order",
            ["Default", "Price: Low to High", "Price: High to Low", "Name: A to Z", "Ratings: High to Low"]
        )

        # Sorting helpers
        def extract_price(product):
            try:
                price = product["Price"].replace(",", "").strip()
                return float(price) if price.replace('.', '', 1).isdigit() else float('inf')
            except:
                return float('inf')

        def extract_rating(product):
            try:
                rating = product["Ratings"].split(" ")[0]
                return float(rating)
            except:
                return 0.0

        def extract_name(product):
            return product["Product Name"].lower()

        # Sorting logic
        if sort_option == "Price: Low to High":
            products.sort(key=extract_price)
        elif sort_option == "Price: High to Low":
            products.sort(key=extract_price, reverse=True)
        elif sort_option == "Name: A to Z":
            products.sort(key=extract_name)
        elif sort_option == "Ratings: High to Low":
            products.sort(key=extract_rating, reverse=True)

        st.subheader("📦 Scraped Product Details")
        for product in products:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    if "Image URL" in product:
                        st.image(product["Image URL"], width=120)
                with col2:
                    st.markdown(f"**{product['Product Name']}**")
                    st.markdown(f"💰 **Price**: ₹{product['Price']}")
                    st.markdown(f"⭐ **Ratings**: {product['Ratings']}")
                    st.markdown(f"📝 **Description**: {product['Description']}")
                    st.markdown(f"[🔗 Product Link]({product['Product URL']})", unsafe_allow_html=True)
            st.markdown("---")

        st.subheader("🔍 Compare Products Side-by-Side")
        product_options = {f"{p['Product Name']} (₹{p['Price']})": idx for idx, p in enumerate(products)}

        selected_indices = st.multiselect(
            "Select products to compare",
            options=list(product_options.keys()),
            max_selections=4,
        )
        selected_products = [products[product_options[key]] for key in selected_indices]

        if selected_products:
            cols = st.columns(len(selected_products))
            for col, product in zip(cols, selected_products):
                with col:
                    st.image(product.get("Image URL", ""), use_container_width=True)
                    st.markdown(f"**{product['Product Name']}**")
                    st.markdown(f"💸 **Price:** ₹{product['Price']}")
                    st.markdown(f"⭐ **Ratings:** {product['Ratings']}")
                    st.markdown(f"📝 **Description:** {product['Description']}")
                    st.markdown(f"[🔗 View Product]({product['Product URL']})", unsafe_allow_html=True)

        with st.expander("🧾 View Search Metadata"):
            st.json(metadata)

        df = pd.DataFrame(products)
        st.subheader("📄 Scraped Data Table")
        st.dataframe(df)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name=f"amazon_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

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
            search_query = generate_search_query(category, product_name, brand)
        else:
            st.error("Please enter a category or Flipkart URL.")
            st.stop()

        with st.spinner("Scraping Flipkart..."):
            products, metadata = scrape_flipkart(search_query)

        if "error" in metadata:
            st.error(metadata["error"])
        elif products:
            df = pd.DataFrame(products)

            # Results Table
            st.subheader("Scraped Results")
            st.dataframe(df)

            # CSV Download
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=f"flipkart_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

            # Comparison Container
            st.subheader("Compare Products Side-by-Side")
            product_names = [p["Product Name"] for p in products]
            selected_names = st.multiselect("Select up to 4 products to compare", product_names, max_selections=4)

            if selected_names:
                selected_products = [p for p in products if p["Product Name"] in selected_names]
                cols = st.columns(len(selected_products))
                for col, product in zip(cols, selected_products):
                    with col:
                        st.image(product.get("Image URL", ""), use_column_width=True)
                        st.markdown(f"**{product['Product Name']}**")
                        st.markdown(f"💰 **Price:** {product['Price']}")
                        st.markdown(f"⭐ **Ratings:** {product['Ratings']}")
                        st.markdown(f"📝 **Description:** {product['Description']}")
                        st.markdown(f"[🔗 Product Link]({product['Product URL']})", unsafe_allow_html=True)

            # Metadata Dropdown
            with st.expander("📊 View Metadata"):
                st.json(metadata)

        else:
            st.warning("No products found. Try modifying your search.")

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
import copy
import streamlit as st

# ============================================================
# MUST be the very first Streamlit call — nothing else above
# ============================================================
st.set_page_config(layout="wide", page_title="EchoSift")

import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image
from requests.exceptions import RequestException

# ---------------------------------------------------------------------------
# Session state — initialise ALL keys before any widget is rendered
# ---------------------------------------------------------------------------

_DEFAULTS: dict = {
    "scraped_results": None,
    "scraped_content": "",
    "scraped_title": "",
    "scraped_summary": "",
    "pdf_text": "",
    "pdf_metadata": {},
    "pdf_summary": "",
    "pdf_qa_history": [],
    "amazon_products": None,
    "amazon_metadata": {},
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = copy.deepcopy(_v)

_WEB_KEYS = ["scraped_results", "scraped_content", "scraped_title", "scraped_summary"]
_PDF_KEYS = ["pdf_text", "pdf_metadata", "pdf_summary", "pdf_qa_history"]
_AMZ_KEYS = ["amazon_products", "amazon_metadata"]


def _reset(keys: list) -> None:
    for k in keys:
        st.session_state[k] = copy.deepcopy(_DEFAULTS[k])


# ---------------------------------------------------------------------------
# Lazy imports for packages that touch Streamlit internals at import time
# ---------------------------------------------------------------------------

def _lottie_widget(anim: dict, key: str) -> None:
    try:
        from streamlit_lottie import st_lottie
        st_lottie(anim, speed=1, height=100, key=key)
    except Exception:
        pass


def _load_lottie(url: str) -> dict | None:
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _header(lottie_url: str, title: str, lottie_key: str) -> None:
    col1, col2 = st.columns([1, 7])
    anim = _load_lottie(lottie_url)
    if anim:
        with col1:
            _lottie_widget(anim, lottie_key)
    with col2:
        st.title(title)


# ---------------------------------------------------------------------------
# Sidebar navigation — option_menu imported lazily inside try/except
# ---------------------------------------------------------------------------

try:
    from streamlit_option_menu import option_menu
    with st.sidebar:
        page = option_menu(
            "Main Menu",
            ["Web Scraping", "PDF Extraction", "Amazon Scraper", "Flipkart Scraper", "Telegram Bot"],
            icons=["cloud", "file-earmark-pdf", "amazon", "cart", "chat-dots"],
            menu_icon="cast",
            default_index=0,
        )
except Exception:
    with st.sidebar:
        page = st.radio(
            "Navigate",
            ["Web Scraping", "PDF Extraction", "Amazon Scraper", "Flipkart Scraper", "Telegram Bot"],
        )

# ---------------------------------------------------------------------------
# Config values — imported after all st.* setup is done
# ---------------------------------------------------------------------------

try:
    from config import LOTTIE_WEB_URL, LOTTIE_AMAZON_URL, LOTTIE_FLIPKART_URL, TELEGRAM_BOT_LINK
except Exception:
    LOTTIE_WEB_URL = LOTTIE_AMAZON_URL = LOTTIE_FLIPKART_URL = ""
    TELEGRAM_BOT_LINK = "#"

# ---------------------------------------------------------------------------
# EchoSift modules — imported after Streamlit is fully initialised
# ---------------------------------------------------------------------------

try:
    from echosift.Scrappers.websitescrape import scrape_website
    from echosift.Scrappers.amazonscrape import scrape_amazon, generate_search_query as amazon_search_query
    from echosift.Scrappers.flipkartscrape import scrape_flipkart, generate_search_query as flipkart_search_query
    from echosift.Extractor.pdfextract import extract_text_from_pdf
    from echosift.Model.modelfunctions import (
        summarize_website_text,
        ask_website_question,
        summarize_pdf_text,
        ask_pdf_question,
    )
    _modules_ok = True
except Exception as _e:
    st.error(f"Failed to load EchoSift modules: {_e}")
    _modules_ok = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _price_sort_key(p: dict) -> float:
    try:
        return float(p["Price"].replace(",", "").strip())
    except Exception:
        return float("inf")


def _rating_sort_key(p: dict) -> float:
    try:
        return float(p["Ratings"].split()[0])
    except Exception:
        return 0.0


def _render_product_card(product: dict) -> None:
    with st.container():
        col_img, col_info = st.columns([1, 4])
        with col_img:
            if product.get("Image URL"):
                st.image(product["Image URL"], width=120)
        with col_info:
            st.markdown(f"**{product['Product Name']}**")
            st.markdown(f"💰 **Price**: ₹{product['Price']}")
            st.markdown(f"⭐ **Ratings**: {product['Ratings']}")
            st.markdown(f"📝 **Description**: {product['Description']}")
            st.markdown(f"[🔗 Product Link]({product['Product URL']})", unsafe_allow_html=True)
    st.markdown("---")


if not _modules_ok:
    st.stop()


# ===========================================================================
# Pages
# ===========================================================================

# ---------------------------------------------------------------------------
# Web Scraping
# ---------------------------------------------------------------------------

if page == "Web Scraping":
    _header(LOTTIE_WEB_URL, "Data Extraction from Web", "web_lottie")

    st.subheader("Web Scraping Functionality")
    st.write("""
    **Steps:**
    1. Enter the URL of the website you wish to scrape.
    2. Set the maximum depth of pages to scrape.
    3. Click **Scrape Website** to extract content.
    4. View extracted content, metadata, response headers, and images.
    5. Optionally summarize or ask questions about the scraped content.
    """)

    url = st.text_input("Enter a URL to scrape", placeholder="https://example.com")
    max_depth = st.slider("Scraping depth", min_value=1, max_value=5, value=2)

    col_scrape, col_summarize, col_reset = st.columns(3)

    with col_scrape:
        if st.button("Scrape Website"):
            if url.strip():
                with st.spinner("Scraping website…"):
                    results = scrape_website(url, max_depth=max_depth)
                if results:
                    st.session_state["scraped_results"] = results
                    st.session_state["scraped_content"] = "\n\n".join(
                        r.get("content", "") for r in results
                    )
                    st.session_state["scraped_title"] = results[0].get("title", "")
                    st.session_state["scraped_summary"] = ""
                else:
                    st.error("No data found or an error occurred.")
            else:
                st.error("Please enter a valid URL.")

    with col_summarize:
        if st.button("Summarize Scraped Content"):
            if st.session_state["scraped_content"]:
                with st.spinner("Generating summary…"):
                    st.session_state["scraped_summary"] = summarize_website_text(
                        st.session_state["scraped_content"]
                    )
            else:
                st.warning("No scraped content yet. Scrape a website first.")

    with col_reset:
        if st.button("Reset All"):
            _reset(_WEB_KEYS)

    if st.session_state["scraped_results"]:
        all_results = st.session_state["scraped_results"]
        titles = [r.get("title", f"Page {i+1}") for i, r in enumerate(all_results)]

        st.subheader("🔍 Filter Scraped Content")
        selected_title = st.selectbox("Filter by Page Title", ["All Pages"] + titles)
        keyword_filter = st.text_input("Filter by Keyword in Content", "")

        filtered = [
            r for i, r in enumerate(all_results)
            if (selected_title == "All Pages" or r.get("title", f"Page {i+1}") == selected_title)
            and (not keyword_filter or keyword_filter.lower() in r.get("content", "").lower())
        ]

        col_data, col_summary = st.columns(2)

        with col_data:
            st.subheader("📝 Extracted Content")
            st.write("\n\n".join(r.get("content", "") for r in filtered) or "No content found.")

            st.subheader("🧾 Metadata & Response Details")
            with st.expander("View Combined Metadata & Response Info"):
                for i, r in enumerate(filtered, 1):
                    st.markdown(f"### Page {i}: {r.get('title', 'No Title')}")
                    st.json({**r.get("metadata", {}), **r.get("response_data", {})})

            st.subheader("🖼️ Extracted Images")
            any_images = False
            for r in filtered:
                for img_url in r.get("images", []):
                    try:
                        img_resp = requests.get(img_url, timeout=5)
                        if img_resp.status_code == 200:
                            st.image(
                                Image.open(BytesIO(img_resp.content)),
                                caption=img_url,
                                use_container_width=True,
                            )
                            any_images = True
                    except Exception:
                        continue
            if not any_images:
                st.write("No images found.")

        with col_summary:
            st.subheader("🧠 Summary")
            if st.session_state["scraped_summary"]:
                st.markdown(
                    f'<div style="padding:1rem;background:#1c1c1e;border-radius:10px;color:white;">'
                    f'{st.session_state["scraped_summary"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("No summary generated yet.")

            st.markdown("---")
            st.subheader("💬 Ask Questions")
            question = st.text_input("Your question", placeholder="What is the main service?")
            if st.button("Ask") and question.strip():
                with st.spinner("Thinking…"):
                    answer = ask_website_question(
                        st.session_state["scraped_content"][:4000], question
                    )
                    st.markdown(
                        f'<div style="padding:1rem;background:#2c2c2e;border-radius:10px;color:white;">'
                        f'{answer}</div>',
                        unsafe_allow_html=True,
                    )


# ---------------------------------------------------------------------------
# PDF Extraction
# ---------------------------------------------------------------------------

elif page == "PDF Extraction":
    _header(LOTTIE_WEB_URL, "PDF Extraction", "pdf_lottie")

    st.subheader("PDF Extraction Functionality")
    st.write("""
    **Steps:**
    1. Upload a PDF file.
    2. Click **Extract PDF Text** to extract content (OCR used for scanned pages).
    3. Optionally summarize the content or ask questions about it.
    """)

    col_title, col_rst = st.columns([8, 1])
    with col_rst:
        if st.button("🔄 Reset"):
            _reset(_PDF_KEYS)

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file and st.button("Extract PDF Text"):
        with st.spinner("Extracting text from PDF…"):
            pdf_bytes = uploaded_file.read()
            text, metadata = extract_text_from_pdf(pdf_bytes)
            st.session_state["pdf_text"] = text
            st.session_state["pdf_metadata"] = metadata
            st.session_state["pdf_summary"] = ""
            st.session_state["pdf_qa_history"] = []

    if st.session_state["pdf_text"]:
        col_pdf, col_ai = st.columns(2)

        with col_pdf:
            st.subheader("📄 Extracted Text")
            st.text_area("PDF Content", st.session_state["pdf_text"], height=400)
            with st.expander("🧾 PDF Metadata"):
                st.json(st.session_state["pdf_metadata"])

        with col_ai:
            st.subheader("🧠 Summary")
            if st.button("Summarize PDF"):
                with st.spinner("Generating summary…"):
                    st.session_state["pdf_summary"] = summarize_pdf_text(
                        st.session_state["pdf_text"]
                    )

            if st.session_state["pdf_summary"]:
                st.markdown(
                    f'<div style="padding:1rem;background:#1c1c1e;border-radius:10px;color:white;">'
                    f'{st.session_state["pdf_summary"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("No summary generated yet.")

            st.markdown("---")
            st.subheader("💬 Ask Questions")
            pdf_question = st.text_input("Your question about the PDF")
            if st.button("Ask PDF") and pdf_question.strip():
                with st.spinner("Thinking…"):
                    answer = ask_pdf_question(st.session_state["pdf_text"], pdf_question)
                    st.session_state["pdf_qa_history"].append({"Q": pdf_question, "A": answer})

            for qa in st.session_state["pdf_qa_history"]:
                st.markdown(f"**Q:** {qa['Q']}")
                st.markdown(
                    f'<div style="padding:.5rem 1rem;background:#2c2c2e;border-radius:8px;color:white;">'
                    f'{qa["A"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("")


# ---------------------------------------------------------------------------
# Amazon Scraper
# ---------------------------------------------------------------------------

elif page == "Amazon Scraper":
    _header(LOTTIE_AMAZON_URL, "Amazon Scraper", "amazon_lottie")

    st.subheader("Instructions")
    st.write("""
    **Steps:**
    1. Enter **Category**, **Product Name**, and/or **Brand**.
    2. Click **Scrape Amazon** to retrieve product listings.
    3. Sort, filter, compare, and download results.
    """)

    category     = st.text_input("Category (e.g. Electronics)")
    product_name = st.text_input("Product Name (e.g. Laptop)")
    brand        = st.text_input("Brand (e.g. Dell)")

    col_btn, col_rst = st.columns([4, 1])
    with col_btn:
        scrape_clicked = st.button("Scrape Amazon")
    with col_rst:
        if st.button("🔄 Reset", key="amz_reset"):
            _reset(_AMZ_KEYS)

    if scrape_clicked:
        if not (category or product_name or brand):
            st.error("Please enter at least one search field.")
        else:
            query = amazon_search_query(category, product_name, brand)
            with st.spinner("Scraping Amazon…"):
                products, metadata = scrape_amazon(query)
            if "error" in metadata:
                st.error(metadata["error"])
            elif products:
                st.session_state["amazon_products"] = products
                st.session_state["amazon_metadata"] = metadata
            else:
                st.warning("No products found.")

    if st.session_state["amazon_products"]:
        full_products = list(st.session_state["amazon_products"])

        sort_option = st.selectbox(
            "Sort by",
            ["Default", "Price: Low to High", "Price: High to Low", "Name: A to Z", "Ratings: High to Low"],
        )
        if sort_option == "Price: Low to High":
            full_products.sort(key=_price_sort_key)
        elif sort_option == "Price: High to Low":
            full_products.sort(key=_price_sort_key, reverse=True)
        elif sort_option == "Name: A to Z":
            full_products.sort(key=lambda p: p["Product Name"].lower())
        elif sort_option == "Ratings: High to Low":
            full_products.sort(key=_rating_sort_key, reverse=True)

        show_top5 = st.checkbox("Show only top 5 products", value=True)
        display   = full_products[:5] if show_top5 else full_products

        st.subheader(f"📦 {'Top 5' if show_top5 else 'All'} Products")
        for p in display:
            _render_product_card(p)

        st.subheader("🔍 Compare Products Side-by-Side")
        options  = {f"{p['Product Name']} (₹{p['Price']})": i for i, p in enumerate(full_products)}
        selected = st.multiselect("Select products to compare", list(options.keys()), max_selections=4)
        if selected:
            cols = st.columns(len(selected))
            for col, key in zip(cols, selected):
                p = full_products[options[key]]
                with col:
                    if p.get("Image URL"):
                        st.image(p["Image URL"], use_container_width=True)
                    st.markdown(f"**{p['Product Name']}**")
                    st.markdown(f"💸 ₹{p['Price']}")
                    st.markdown(f"⭐ {p['Ratings']}")
                    st.markdown(f"[🔗 View]({p['Product URL']})", unsafe_allow_html=True)

        with st.expander("🧾 Search Metadata"):
            st.json(st.session_state["amazon_metadata"])

        df = pd.DataFrame(full_products)
        st.subheader("📄 Data Table")
        st.dataframe(df)
        st.download_button(
            "⬇️ Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            f"amazon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
        )


# ---------------------------------------------------------------------------
# Flipkart Scraper
# ---------------------------------------------------------------------------

elif page == "Flipkart Scraper":
    _header(LOTTIE_FLIPKART_URL, "Flipkart Scraper", "flipkart_lottie")

    st.subheader("Instructions")
    st.write("""
    **Steps:**
    1. **Option A:** Enter category / product / brand to auto-build a query.
    2. **Option B:** Paste a direct Flipkart URL.
    3. Click **Scrape Flipkart** to retrieve listings.
    """)

    flipkart_url = st.text_input("Flipkart URL (optional)")
    category     = st.text_input("Category (optional)")
    product_name = st.text_input("Product Name (optional)")
    brand        = st.text_input("Brand (optional)")

    if st.button("Scrape Flipkart"):
        if flipkart_url:
            query = flipkart_url
        elif category or product_name or brand:
            query = flipkart_search_query(category, product_name, brand)
        else:
            st.error("Please enter a category or Flipkart URL.")
            st.stop()

        with st.spinner("Scraping Flipkart…"):
            products, metadata = scrape_flipkart(query)

        if "error" in metadata:
            st.error(metadata["error"])
        elif products:
            df = pd.DataFrame(products)
            st.subheader("Scraped Results")
            st.dataframe(df)
            st.download_button(
                "Download as CSV",
                df.to_csv(index=False).encode("utf-8"),
                f"flipkart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
            )

            st.subheader("Compare Products Side-by-Side")
            names    = [p["Product Name"] for p in products]
            selected = st.multiselect("Select up to 4 products", names, max_selections=4)
            if selected:
                sel_products = [p for p in products if p["Product Name"] in selected]
                cols = st.columns(len(sel_products))
                for col, p in zip(cols, sel_products):
                    with col:
                        if p.get("Image URL"):
                            st.image(p["Image URL"], use_container_width=True)
                        st.markdown(f"**{p['Product Name']}**")
                        st.markdown(f"💰 {p['Price']}")
                        st.markdown(f"⭐ {p['Ratings']}")
                        st.markdown(f"[🔗 View]({p['Product URL']})", unsafe_allow_html=True)

            with st.expander("📊 View Metadata"):
                st.json(metadata)
        else:
            st.warning("No products found. Try a different search.")


# ---------------------------------------------------------------------------
# Telegram Bot
# ---------------------------------------------------------------------------

elif page == "Telegram Bot":
    _header(LOTTIE_WEB_URL, "Telegram Bot", "telegram_lottie")

    st.subheader("Telegram Bot Integration")
    st.write("""
    **Steps:**
    1. Use the EchoSift Telegram bot to interact with data extraction.
    2. Send URLs or PDFs to the bot and receive extracted or summarized content.
    """)
    st.write(f"**Bot Link:** [{TELEGRAM_BOT_LINK}]({TELEGRAM_BOT_LINK})")
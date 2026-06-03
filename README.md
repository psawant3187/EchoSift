<div align="center">

# 🔊 EchoSift

### AI-Powered Data Extraction & Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4.1_mini-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Selenium](https://img.shields.io/badge/Selenium-4.31-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**EchoSift** is an intelligent data extraction platform that scrapes websites, Amazon, and Flipkart — then uses Azure OpenAI (GPT-4.1 mini) to summarize content, answer questions, and extract insights from PDFs. All wrapped in a beautiful Streamlit UI with a companion Telegram bot.

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Configuration](#-configuration) • [Usage](#-usage) • [Project Structure](#-project-structure) • [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

| Module | Capabilities |
|---|---|
| 🌐 **Web Scraper** | Multi-depth recursive crawling, language detection, metadata extraction, image scraping, AI summarization & Q&A |
| 📄 **PDF Extractor** | Text extraction with OCR fallback (Tesseract), metadata parsing, AI summarization & Q&A |
| 🛒 **Amazon Scraper** | Product listings, prices, ratings, images, sort/filter/compare, CSV export |
| 🏪 **Flipkart Scraper** | Selenium-powered scraping, product comparison, CSV export |
| 🤖 **Telegram Bot** | Interact with EchoSift from Telegram — send URLs or PDFs, receive extracted content |

---

## 🏗️ Architecture

```
EchoSift/
│
├── EchoSift.py                  ← Main Streamlit app (entry point)
├── config.py                    ← All configuration (API keys, URLs, limits)
├── config.toml                  ← Streamlit theme config
├── requirements.txt
│
└── echosift/                    ← Core package
    ├── __init__.py
    │
    ├── Scrappers/
    │   ├── websitescrape.py     ← Recursive multi-threaded web scraper
    │   ├── amazonscrape.py      ← Amazon India product scraper (requests + BS4)
    │   └── flipkartscrape.py    ← Flipkart scraper (Selenium + BS4)
    │
    ├── Extractor/
    │   └── pdfextract.py        ← PDF text extraction + Tesseract OCR fallback
    │
    └── Model/
        ├── client.py            ← Azure OpenAI client initialisation
        └── modelfunctions.py    ← GPT-4.1 mini summarization & Q&A functions
```

### Data Flow

```
User Input (URL / PDF / Search)
        │
        ▼
  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐
  │  Scrapper / │───▶│  Extracted   │───▶│  Azure OpenAI │
  │  Extractor  │    │  Raw Text    │    │  GPT-4.1 mini │
  └─────────────┘    └──────────────┘    └───────────────┘
        │                                        │
        ▼                                        ▼
  Metadata, Images,                    Summary / Answer
  Product Data, CSV
```

---

## 🖥️ Screenshots

### 🌐 Web Scraping Page
```
┌────────────────────────────────────────────────────────────────────┐
│  🔊 EchoSift          [Web Scraping]                               │
│ ─────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Enter a URL to scrape:  [ https://example.com           ]  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  Scraping depth: ──●────────────────  2                            │
│                                                                    │
│  [Scrape Website]   [Summarize Content]   [Reset All]              │
│                                                                    │
│  🔍 Filter Scraped Content                                         │
│  ┌──────────────────────────┐  ┌─────────────────────────────┐    │
│  │  📝 Extracted Content    │  │  🧠 AI Summary              │    │
│  │                          │  │                             │    │
│  │  Welcome to Example...   │  │  ┌─────────────────────┐   │    │
│  │  This domain is for      │  │  │ This page describes  │   │    │
│  │  use in illustrative     │  │  │ an example domain... │   │    │
│  │  examples...             │  │  └─────────────────────┘   │    │
│  │                          │  │                             │    │
│  │  🧾 Metadata             │  │  💬 Ask Questions           │    │
│  │  🖼️ Images               │  │  [Your question...    ] Ask │    │
│  └──────────────────────────┘  └─────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

### 📄 PDF Extraction Page
```
┌────────────────────────────────────────────────────────────────────┐
│  📄 PDF Extraction                               [🔄 Reset]        │
│ ─────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  📎 Upload a PDF file     [  Drop file here or Browse  ]    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    [Extract PDF Text]                               │
│                                                                    │
│  ┌──────────────────────────┐  ┌─────────────────────────────┐    │
│  │  📄 Extracted Text       │  │  🧠 Summary                 │    │
│  │                          │  │  [Summarize PDF]            │    │
│  │  ┌────────────────────┐  │  │                             │    │
│  │  │ Page 1 content...  │  │  │  ┌─────────────────────┐   │    │
│  │  │ Lorem ipsum dolor  │  │  │  │ This PDF contains   │   │    │
│  │  │ sit amet...        │  │  │  │ information about.. │   │    │
│  │  └────────────────────┘  │  │  └─────────────────────┘   │    │
│  │                          │  │                             │    │
│  │  ▶ PDF Metadata          │  │  💬 Ask Questions           │    │
│  └──────────────────────────┘  └─────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

### 🛒 Amazon Scraper Page
```
┌────────────────────────────────────────────────────────────────────┐
│  🛒 Amazon Scraper                                                 │
│ ─────────────────────────────────────────────────────────────────  │
│  Category:     [ Electronics              ]                        │
│  Product Name: [ Laptop                   ]                        │
│  Brand:        [ Dell                     ]                        │
│                                                                    │
│  [Scrape Amazon]                              [🔄 Reset]           │
│                                                                    │
│  Sort by: [Price: Low to High ▼]  ☑ Show only top 5 products      │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ 🖼️  Dell Inspiron 15 3530                                  │   │
│  │     💰 Price: ₹54,990   ⭐ Ratings: 4.2 out of 5 stars    │   │
│  │     📝 Dell Inspiron 15 3530 Laptop, Intel Core i5...      │   │
│  │     🔗 Product Link                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  🔍 Compare Products Side-by-Side                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│  │ 🖼️ Product A │ │ 🖼️ Product B │ │ 🖼️ Product C │              │
│  │ ₹54,990      │ │ ₹62,499      │ │ ₹45,000      │              │
│  │ ⭐ 4.2       │ │ ⭐ 4.5       │ │ ⭐ 3.9       │              │
│  └──────────────┘ └──────────────┘ └──────────────┘              │
│                                                                    │
│  [⬇️ Download as CSV]                                              │
└────────────────────────────────────────────────────────────────────┘
```

### 🏪 Flipkart Scraper Page
```
┌────────────────────────────────────────────────────────────────────┐
│  🏪 Flipkart Scraper                                               │
│ ─────────────────────────────────────────────────────────────────  │
│  Flipkart URL (optional): [ https://www.flipkart.com/...  ]        │
│  Category:                [ Smartphones               ]            │
│  Product Name:            [ Samsung Galaxy            ]            │
│  Brand:                   [ Samsung                   ]            │
│                                                                    │
│  [Scrape Flipkart]                                                 │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Product Name        │ Price    │ Ratings │ URL             │   │
│  │ ─────────────────── │ ──────── │ ─────── │ ─────────────── │   │
│  │ Samsung Galaxy A55  │ ₹38,999  │ 4.3     │ 🔗 View         │   │
│  │ Samsung Galaxy S24  │ ₹74,999  │ 4.6     │ 🔗 View         │   │
│  └────────────────────────────────────────────────────────────┘   │
│  [Download as CSV]                                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Installation

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Required |
| Google Chrome | Latest | For Flipkart scraping |
| Tesseract OCR | 5.x | For scanned PDF support |
| Azure OpenAI | — | API key required |

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/EchoSift.git
cd EchoSift
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
```
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
Default install path: C:\Program Files\Tesseract-OCR\tesseract.exe
```

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

### 5. Fix websocket conflict (if you see a Selenium import error)

```bash
pip uninstall websocket websocket-client -y
pip install websocket-client
```

---

## 🔧 Configuration

All configuration lives in **`config.py`**. Sensitive values are read from environment variables with sensible defaults.

### Required: Azure OpenAI

Set these environment variables (or edit `config.py` directly for local dev):

```bash
# Windows (PowerShell)
$env:AZURE_OPENAI_API_KEY    = "your-api-key"
$env:AZURE_OPENAI_ENDPOINT   = "https://your-resource.cognitiveservices.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
$env:AZURE_OPENAI_API_VERSION = "2025-01-01-preview"

# macOS / Linux
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"
export AZURE_OPENAI_API_VERSION="2025-01-01-preview"
```

### Optional: Tesseract Path

If Tesseract is installed in a non-default location:

```bash
export TESSERACT_CMD="/usr/bin/tesseract"      # Linux/macOS
$env:TESSERACT_CMD = "C:\custom\path\tesseract.exe"  # Windows
```

### All Configuration Options

| Variable | Default | Description |
|---|---|---|
| `AZURE_OPENAI_API_KEY` | — | **Required.** Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | — | **Required.** Azure resource endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4.1-mini` | Deployment name |
| `AZURE_OPENAI_API_VERSION` | `2025-01-01-preview` | API version |
| `SCRAPE_MAX_DEPTH` | `5` | Max recursion depth for web scraping |
| `SCRAPE_MAX_LINKS_PER_PAGE` | `100` | Max links followed per page |
| `SCRAPE_MAX_WORKERS` | `10` | Parallel scraping threads |
| `SCRAPE_TIMEOUT_SECONDS` | `10` | HTTP request timeout |
| `PDF_MAX_PAGE_EXTRACT` | `50` | Max pages extracted per PDF |
| `TESSERACT_CMD` | Windows default path | Path to tesseract binary |
| `MODEL_MAX_INPUT_TOKENS` | `4000` | Max chars sent to model |
| `MODEL_MAX_COMPLETION_TOKENS` | `16384` | Max tokens in model response |
| `SCRAPER_PAGE_LOAD_WAIT` | `3` | Seconds to wait for JS render (Flipkart) |

---

## 🚀 Running the App

```bash
streamlit run EchoSift.py
```

The app opens automatically at **http://localhost:8501**

---

## 📖 Usage Guide

### 🌐 Web Scraping

1. Navigate to **Web Scraping** in the sidebar
2. Enter a URL (e.g. `https://docs.python.org`)
3. Set the **scraping depth** (1 = homepage only, 5 = deep crawl)
4. Click **Scrape Website** — content, metadata, and images are extracted
5. Filter results by page title or keyword
6. Click **Summarize Scraped Content** to get an AI summary
7. Use the **Ask Questions** box to query the content with GPT-4.1 mini

> ⚠️ Higher depth values crawl more pages and take longer. Depth 2–3 is recommended for most sites.

### 📄 PDF Extraction

1. Navigate to **PDF Extraction**
2. Upload a `.pdf` file using the file uploader
3. Click **Extract PDF Text**
   - Text-based pages are extracted directly via `pdfplumber`
   - Image-based/scanned pages automatically fall back to **Tesseract OCR**
4. View extracted text and PDF metadata
5. Click **Summarize PDF** for an AI-generated summary
6. Ask questions about the document in the Q&A box — history is maintained per session

### 🛒 Amazon Scraper

1. Navigate to **Amazon Scraper**
2. Fill in any combination of **Category**, **Product Name**, **Brand**
3. Click **Scrape Amazon**
4. Results appear as product cards — sort by price, rating, or name
5. Toggle **Show only top 5** to focus on the best results
6. Use **Compare Products Side-by-Side** (up to 4 products)
7. Download full results as a CSV

> ℹ️ Amazon scraping uses `requests` + BeautifulSoup. No browser required.

### 🏪 Flipkart Scraper

1. Navigate to **Flipkart Scraper**
2. Either:
   - **Option A:** Fill in Category / Product Name / Brand (auto-builds query)
   - **Option B:** Paste a direct Flipkart search URL
3. Click **Scrape Flipkart** (launches headless Chrome via Selenium)
4. Browse results, compare up to 4 products side-by-side, and download CSV

> ℹ️ Flipkart uses JavaScript rendering, so Selenium + Chrome is required.

### 🤖 Telegram Bot

1. Navigate to **Telegram Bot** in the sidebar
2. Open the bot link: [https://t.me/EchoSiftBot](https://t.me/EchoSiftBot)
3. Send a URL → receive extracted & summarized content
4. Send a PDF → receive extracted text and summary

---

## 📦 Project Structure

```
EchoSift/
│
├── EchoSift.py                   ← Streamlit UI — all 5 pages
├── config.py                     ← Centralised config & env vars
├── config.toml                   ← Streamlit theme (dark mode etc.)
├── requirements.txt              ← Python dependencies
├── EchoSift.gif                  ← Demo animation
│
└── echosift/
    ├── __init__.py
    │
    ├── Scrappers/
    │   ├── websitescrape.py      ← scrape_website() — recursive, threaded
    │   │                            Uses: requests, BeautifulSoup, Goose3,
    │   │                                  langdetect, tldextract
    │   │
    │   ├── amazonscrape.py       ← scrape_amazon(), generate_search_query()
    │   │                            Uses: requests, BeautifulSoup
    │   │
    │   └── flipkartscrape.py     ← scrape_flipkart(), generate_search_query()
    │                                Uses: Selenium, webdriver-manager, BS4
    │
    ├── Extractor/
    │   └── pdfextract.py         ← extract_text_from_pdf()
    │                                Uses: pdfplumber, pytesseract (OCR fallback)
    │
    └── Model/
        ├── client.py             ← AzureOpenAI client singleton
        └── modelfunctions.py     ← summarize_*(), ask_*() using GPT-4.1 mini
```

---

## 📋 Requirements

```
beautifulsoup4==4.13.4
goose3==3.1.19
langdetect==1.0.9
openai==1.75.0
pandas==2.2.3
Pillow==11.2.1
pymupdf==1.25.5
pytesseract==0.3.13
Requests==2.32.3
selenium==4.31.0
streamlit==1.41.1
streamlit_lottie==0.0.5
streamlit_option_menu==0.4.0
tldextract==5.1.3
webdriver_manager==4.0.2
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### `Bad message format: Tried to use SessionInfo before it was initialized`

This is a Streamlit internal timing issue. **Fix:** ensure `st.set_page_config()` is the very first Streamlit call in `EchoSift.py` and that no `st.rerun()` is called inside button handlers. The provided fixed `EchoSift.py` resolves this.

### `ImportError: cannot import name 'WebSocketApp' from 'websocket'`

Two conflicting websocket packages are installed. Fix:
```bash
pip uninstall websocket websocket-client -y
pip install websocket-client
pip install --upgrade selenium
```

### Flipkart scraper returns no results

Flipkart's CSS class names change periodically. The scraper targets:
- `_1AtVbE` (product card container)
- `s1Q9rs`, `IRpwTa`, `_4rR01T` (product name)
- `_30jeq3 _1_WHN1`, `_30jeq3` (price)
- `_3LWZlK` (rating)

If Flipkart updates their UI, these class names may need to be updated in `flipkartscrape.py`.

### PDF OCR returns empty or garbled text

- Ensure Tesseract is installed and `TESSERACT_CMD` points to the correct binary
- For non-English PDFs, install the relevant Tesseract language pack:
  ```bash
  # Example for Hindi
  sudo apt install tesseract-ocr-hin
  ```

### Scraping is very slow

Reduce `SCRAPE_MAX_DEPTH` and `SCRAPE_MAX_LINKS_PER_PAGE` in `config.py` or via environment variables. For most use cases, depth 2 with 20–30 links per page is sufficient.

### Chrome not found (Flipkart)

`webdriver-manager` auto-downloads ChromeDriver, but Chrome itself must be installed:
- **Windows/macOS:** Install from https://www.google.com/chrome/
- **Ubuntu:**
  ```bash
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  sudo apt install google-chrome-stable
  ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using **Streamlit** · **Azure OpenAI** · **Selenium** · **BeautifulSoup**

</div>

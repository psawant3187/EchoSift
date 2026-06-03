import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project Root
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUTPUT_DIR = str(BASE_DIR / "output")

# ---------------------------------------------------------------------------
# Azure OpenAI
# ---------------------------------------------------------------------------
AZURE_OPENAI_API_KEY    = os.getenv("AZURE_OPENAI_API_KEY",    "YOUR_API_KEY_HERE")
AZURE_OPENAI_ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT",   "YOUR_API_ENDPOINT_HERE")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "YOUR_MODEL_NAME")
AZURE_OPENAI_API_VERSION    = os.getenv("AZURE_OPENAI_API_VERSION", "MODEL_VERSION")

# ---------------------------------------------------------------------------
# Web Scraping
# ---------------------------------------------------------------------------
SCRAPE_MAX_DEPTH          = int(os.getenv("SCRAPE_MAX_DEPTH",          "5"))
SCRAPE_MAX_LINKS_PER_PAGE = int(os.getenv("SCRAPE_MAX_LINKS_PER_PAGE", "100"))
SCRAPE_MAX_WORKERS        = int(os.getenv("SCRAPE_MAX_WORKERS",        "10"))
SCRAPE_TIMEOUT_SECONDS    = int(os.getenv("SCRAPE_TIMEOUT_SECONDS",    "10"))

# ---------------------------------------------------------------------------
# PDF Extraction
# ---------------------------------------------------------------------------
PDF_MAX_PAGE_EXTRACT = int(os.getenv("PDF_MAX_PAGE_EXTRACT", "50"))
TESSERACT_CMD        = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Windows default; override via env
)

# ---------------------------------------------------------------------------
# AI / Model
# ---------------------------------------------------------------------------
MODEL_MAX_INPUT_TOKENS      = int(os.getenv("MODEL_MAX_INPUT_TOKENS",  "4000"))
MODEL_MAX_COMPLETION_TOKENS = int(os.getenv("MODEL_MAX_COMPLETION_TOKENS", "16384"))

# ---------------------------------------------------------------------------
# Product Scrapers
# ---------------------------------------------------------------------------
AMAZON_BASE_URL   = "https://www.amazon.in"
FLIPKART_BASE_URL = "https://www.flipkart.com"
SCRAPER_PAGE_LOAD_WAIT = int(os.getenv("SCRAPER_PAGE_LOAD_WAIT", "3"))  # seconds

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
]

INDIAN_LANG_CODES = ["hi", "bn", "te", "mr", "ta", "gu", "kn", "ml", "pa", "ur"]

# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
LOTTIE_WEB_URL      = "https://lottie.host/99a68a00-6e33-43fb-9ee6-cccc4c19131d/YcyAardQqk.json"
LOTTIE_AMAZON_URL   = "https://lottie.host/8ef544f8-2f05-4f15-90a9-64652158ae6a/BSZPC5XVB5.json"
LOTTIE_FLIPKART_URL = "https://lottie.host/8ef544f8-2f05-4f15-90a9-64652158ae6a/BSZPC5XVB5.json"

TELEGRAM_BOT_LINK = "https://t.me/EchoSiftBot"

# ---------------------------------------------------------------------------
# Server (future API / backend)
# ---------------------------------------------------------------------------
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
from echosift.Model.client import client
from config import AZURE_OPENAI_DEPLOYMENT, MODEL_MAX_INPUT_TOKENS, MODEL_MAX_COMPLETION_TOKENS


# ---------------------------------------------------------------------------
# Web content helpers
# ---------------------------------------------------------------------------

def summarize_website_text(text: str) -> str:
    """Summarize scraped website text."""
    if not text.strip():
        return "No text to summarize."
    try:
        truncated = text[:MODEL_MAX_INPUT_TOKENS]
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            max_completion_tokens=MODEL_MAX_COMPLETION_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a summarization agent. Summarize the provided content "
                        "and provide analysis on extracted metadata."
                    ),
                },
                {"role": "user", "content": f"Summarize this:\n{truncated}"},
            ],
        )
        return response.choices[0].message.content or "Summary could not be generated."
    except Exception as e:
        return f"Error summarizing text: {e}"


def ask_website_question(text: str, question: str) -> str:
    """Answer a question about scraped website content."""
    try:
        truncated = text[:MODEL_MAX_INPUT_TOKENS]
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            max_completion_tokens=MODEL_MAX_COMPLETION_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that answers questions based on scraped website content.",
                },
                {"role": "user", "content": f"Content:\n{truncated}\n\nQuestion: {question}"},
            ],
        )
        return response.choices[0].message.content or "No answer generated."
    except Exception as e:
        return f"Error answering question: {e}"


# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

def summarize_pdf_text(text: str) -> str:
    """Summarize text extracted from a PDF."""
    if not text.strip():
        return "No text to summarize."
    try:
        truncated = text[:MODEL_MAX_INPUT_TOKENS]
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            max_completion_tokens=MODEL_MAX_COMPLETION_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that summarizes PDF content and provides "
                        "structured analysis based on extracted metadata."
                    ),
                },
                {"role": "user", "content": f"Summarize the following content:\n{truncated}"},
            ],
        )
        return response.choices[0].message.content or "Summary could not be generated."
    except Exception as e:
        return f"Error summarizing text: {e}"


def ask_pdf_question(text: str, user_query: str) -> str:
    """Answer a question about PDF content."""
    if not text.strip():
        return "No PDF content available for querying."
    if not user_query.strip():
        return "No question provided."
    try:
        truncated = text[:MODEL_MAX_INPUT_TOKENS]
        prompt = (
            f"You are an assistant that answers questions based on PDF content.\n\n"
            f'Content:\n"""{truncated}"""\n\nQuestion:\n{user_query}'
        )
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            max_completion_tokens=MODEL_MAX_COMPLETION_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or "No response from model."
    except Exception as e:
        return f"Error during Q&A: {e}"
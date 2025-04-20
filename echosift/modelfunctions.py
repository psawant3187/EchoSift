import openai 
API_KEY = "ddc-bUOZrLV5gJb4KLXJwnDmaFaS6pd7NcaewGsaaTLV9NWHC7Srmj"
BASE_URL = "https://api.sree.shop/v1"
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Summarization function
def summarize_website_text(text: str) -> str:
    MAX_TOKENS = 4000  # Adjust based on API limits
    try:
        if not text.strip():
            return "No text to summarize."
        
        truncated_text = text[:MAX_TOKENS]  # Limit input size
        response = client.chat.completions.create(
            model="Meta-Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": f"Summarize this: {truncated_text} also provide analysis on extract metadata."}]
        )

        return response.choices[0].message.content or "Summary could not be generated."

    except Exception as e:
        return f"Error summarizing text: {e}"
    
#  QnA for Data Extracted from Web
def ask_website_question(text: str, question: str) -> str:
    try:
        truncated_text = text[:4000]  # Safely limit the context
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that answers questions based on scraped website content."},
                {"role": "user", "content": f"Content:\n{truncated_text}\n\nQuestion: {question}"}
            ]
        )
        return response.choices[0].message.content or "No answer generated."
    except Exception as e:
        return f"Error answering question: {e}"

# Summarization function
def summarize_pdf_text(text: str) -> str:
    MAX_TOKENS = 4000  # Adjust based on API limits
    try:
        if not text.strip():
            return "No text to summarize."
        
        truncated_text = text[:MAX_TOKENS]  # Limit input size
        response = client.chat.completions.create(
            model="Meta-Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": f"Summarize this: {truncated_text}"}]
        )

        return response.choices[0].message.content or "Summary could not be generated."

    except Exception as e:
        return f"Error summarizing text: {e}"
    
# QnA Function for PDF Extraction
def ask_pdf_question(text: str, user_query: str) -> str:
    MAX_TOKENS = 4000
    try:
        if not text.strip():
            return "No PDF content available for querying."
        if not user_query.strip():
            return "No question provided."

        truncated_text = text[:MAX_TOKENS]
        prompt = f"""
You are an assistant that answers questions based on PDF content.
Here is the content:
\"\"\"{truncated_text}\"\"\"

Now answer this question:
{user_query}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content or "No response from model."

    except Exception as e:
        return f"Error during QnA: {e}"

    

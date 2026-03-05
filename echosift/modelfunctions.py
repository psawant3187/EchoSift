import os
from openai import AzureOpenAI

# Trial Func
endpoint = "https://echosift-resource.cognitiveservices.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview"
model_name = "gpt-4.1-mini"
deployment = "gpt-4.1-mini"
subscription_key = "6WSCdbLqf8J7fmZSTb3QhhKj4uP1oeTq3WYByzjun8zcE7idccsFJQQJ99CAACHYHv6XJ3w3AAAAACOGixJD"
api_version = "2025-01-01-preview"

client = AzureOpenAI(
    api_version = api_version,
    azure_endpoint = endpoint,
    api_key = subscription_key
)

# Summarization function
def summarize_website_text(text: str) -> str:
    MAX_TOKENS = 4000  # Adjust based on API limits
    try:
        if not text.strip():
            return "No text to summarize."
        
        truncated_text = text[:MAX_TOKENS]  # Limit input size
        # response = client.chat.completions.create(
        #     model="Meta-Llama-3.3-70B-Instruct-Turbo",
        #     messages=[{"role": "user", "content": f"Summarize this: {truncated_text} also provide analysis on extract metadata."}]
        # )
        response = client.chat.completions.create(
            messages = [
        {
            "role" : "system",
            "content" : "You are a summarization agent which will summarize the provided content with relation to the original and summarized content."
        },
        {
            "role" : "user",
            "content" : f"Summarize this:{truncated_text} also provide analysis on extracted metadata."
        }
    ],
    max_completion_tokens = 16384,
    model = deployment,
        )

        return response.choices[0].message.content or "Summary could not be generated."

    except Exception as e:
        return f"Error summarizing text: {e}"

#  QnA for Data Extracted from Web
def ask_website_question(text: str, question: str) -> str:
    try:
        truncated_text = text[:4000]  # Safely limit the context
        response = client.chat.completions.create(
            model= deployment,
            max_completion_tokens= 16384,
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
            model= deployment,
            max_completion_tokens= 16384,
            messages=[
                {
                    "role" : "system",
                    "content" : "You are an assistant who summarizes the content extracted from provided PDFs and also provide analysis based on the metadata ecxtracted from PDFs also provide structured summarized content"
                },
                {"role": "user", 
                    "content": f"Summarize the following content into mid-sized content: {truncated_text}"}]
        )
        summary = response.choices[0].message.content
        return summary or "Summary could not be generated."
        

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
            model= deployment,
            max_completion_tokens= 16384,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content or "No response from model."

    except Exception as e:
        return f"Error during QnA: {e}"

    

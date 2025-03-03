import openai
API_KEY = "ddc-bUOZrLV5gJb4KLXJwnDmaFaS6pd7NcaewGsaaTLV9NWHC7Srmj"
BASE_URL = "https://api.sree.shop/v1"
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Summarization function
def summarize_text(text: str) -> str:
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
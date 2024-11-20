import os,openai
from dotenv import load_dotenv
from rich import print as pprint

def main():

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    response = openai.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages = [
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":"Please write a poem of 200 words that relates to the theme of nature."}
        ],
        max_tokens=20,
    )

    response = response.model_dump()

    pprint(response.get("choices")[0].get("message").get("content"))

if __name__ == "__main__":
    load_dotenv()
    main()


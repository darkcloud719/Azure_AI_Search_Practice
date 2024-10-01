import os, json
import openai
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
            {"role":"system","content":"You are a helpful assistant"},
            {"role":"user","content":"Hello World!!!"}
        ],
        max_tokens=1000
    )

    pprint(response.model_dump())

    pprint(type(response.model_dump()))

    # pprint(response.choices[0].message.content)

    pprint(response.model_dump().get("choices")[0].get("message").get("content"))

if __name__ == "__main__":
    load_dotenv()
    main()
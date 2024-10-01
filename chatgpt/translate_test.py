import os
import openai
from dotenv import load_dotenv
from rich import print as pprint

def main():

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    try:
        response = openai.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages = [
                {"role":"system","content":"You are a translator. Please translate the following sentence to English."},
                {"role":"user","content":"我是一個英文翻譯機器人"}
            ],
            max_tokens=1000
        )
    except openai.APIError as err:
        print(err.message)

    pprint(response.choices[0].message.content)

if __name__ == "__main__":
    load_dotenv()
    main()
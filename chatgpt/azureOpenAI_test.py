import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rich import print as pprint

def main():
    client = AzureOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version = os.getenv("OPENAI_API_VERSION")
    )

    completion = client.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages = [{
            "role":"system","content":"You are a helpful assistant.",
            "role":"user","content":"What is the highest mountain in the world?"
        }]
    )

    pprint(completion.choices[0].message.content)

if __name__ == "__main__":
    load_dotenv()
    main()


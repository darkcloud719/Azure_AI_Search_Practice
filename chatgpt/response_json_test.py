import os
import openai
import json
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
            {"role":"system","content":"You are a helpful assistant,and please response by json."},
            {"role":"user","content":"What is the highest mountain in the Taiwan?"}
        ],
        response_format={"type":"json_object"}
    )

    json_string = response.choices[0].message.content

    dic = json.loads(json_string)

    pprint(response.choices[0].message.content)

    pprint(dic)

    for key, value in dic.items():
        print(f"{key}:{value}")

if __name__ == "__main__":
    load_dotenv()
    main()
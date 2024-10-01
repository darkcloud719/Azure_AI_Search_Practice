import requests
import base64 
import openai
import os
from rich import print as pprint
from dotenv import load_dotenv
# r = requests.get(
#     'https://flagtech.github.io/F3762/images/cat1.jpg'
# )

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def main(img):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    response = openai.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_VISION"),
        messages = [
            {"role":"user","content":[
                {"type":"text","text":"What is in the picture?"},
                {"type":"image_url","image_url":
                    {"url": f"data:image/jpeg;base64,{img}", "detail": "high"}
                }
            ]}
        ],
        max_tokens=300
    )
    pprint(response.choices[0].message.content)


if __name__ == "__main__":
    load_dotenv()
    img = encode_image("cat2.jpg")
    main(img)



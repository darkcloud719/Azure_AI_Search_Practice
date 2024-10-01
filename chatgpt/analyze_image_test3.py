import os, openai, base64, requests
from dotenv import load_dotenv
from rich import print as pprint

def store_image(image_url):
    r = requests.get(image_url)
    with open("cat3.jpg", "wb") as f:
        f.write(r.content)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def main():
    
    img1 = encode_image("cat2.jpg")
    img2 = encode_image("cat3.jpg")

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    response = openai.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_VISION"),
        messages = [
            {"role":"user","content":[
                {"type":"text", "text":"What is the same in the pictures?"},
                {"type":"image_url","image_url":
                    {"url":f"data:image/jpeg;base64,{img1}", "detail":"high"}
                },
                {
                 "type":"image_url","image_url":
                    {"url":f"data:image/jpeg;base64,{img2}", "detail":"high"}
                }
            ]},
        ],
        max_tokens=300
    )

    pprint(response.choices[0].message.content)

if __name__ == "__main__":
    load_dotenv()
    # store_image("https://flagtech.github.io/F3762/images/cat2.jpg")
    main()
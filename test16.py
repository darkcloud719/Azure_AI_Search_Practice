import os,requests,json,openai
from openai import AzureOpenAI
from dotenv import load_dotenv
from PIL import Image

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPONIT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_type = "azure"

def main():

    result = openai.images.generate(
        model = "dall-e-3",
        prompt = "a close-up of a bear walking through the forest",
        n = 1
    )

    json_response = json.loads(result.model_dump_json())

    image_dir = os.path.join(os.curdir,"images_new")

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    image_path = os.path.join(image_dir, "generated_image.png")

    image_url = json_response["data"][0]["url"]
    generated_image = requests.get(image_url).content
    with open(image_path,"wb") as image_file:
        image_file.write(generated_image)

    image = Image.open(image_path)
    image.show()

if __name__ == "__main__":
    load_dotenv()
    main()
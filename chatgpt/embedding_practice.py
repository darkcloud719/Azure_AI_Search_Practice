import os
import openai
from dotenv import load_dotenv
from rich import print as pprint
from openai import AzureOpenAI

# def main():
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#     openai.api_version = os.getenv("OPENAI_API_VERSION")
#     openai.api_type = "azure"

#     response = openai.embeddings.create(
#         model = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"),
#         input = "apple",
#         # input = ["apple","banana"]
#     )

#     pprint(response.data[0].embedding)

# if __name__ == "__main__":
#     load_dotenv()
#     main()

def main():

    client = AzureOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        api_version = os.getenv("OPENAI_API_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    response = client.embeddings.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"),
        input = "Apple"
    )

    pprint(response.data[0].embedding)

if __name__ == "__main__":
    load_dotenv()
    main()

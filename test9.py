import openai
import os 
from rich import print as pprint 
from dotenv import load_dotenv
from openai import AzureOpenAI

# def main():
    
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     openai.api_version = os.getenv("OPENAI_API_VERSION")
#     openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#     openai.api_type = "azure"

#     response = openai.chat.completions.create(
#         model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
#         messages = [{"role":"user","content":"What is the average rating of the applications?"}] 
#     )

#     pprint(response)

# if __name__ == "__main__":
#     load_dotenv()
#     main()

load_dotenv()

# client = AzureOpenAI(
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("OPENAI_API_KEY"),
#     api_version="2024-08-01-preview"
# )

# response = client.chat.completions.create(
#     model = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR"),
#     messages = [{"role":"user","content":"What is the average rating of the application?"}]
# )

print(f"AZURE_OPENAI_ENDPOINT:{os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"OPENAI_API_KEY:{os.getenv('OPENAI_API_KEY')}")
print(f"OPENAI_API_VERSION:{os.getenv('OPENAI_API_VERSION')}")
print(f"AZURE_OPENAI_DEPLOYMENT:{os.getenv('AZURE_OPENAI_DEPLOYMENT')}")

# print(response.choices[0].message.content)
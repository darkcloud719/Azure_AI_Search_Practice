import os
import asyncio
import openai
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from rich import print as pprint

# async def main():

#     client = AsyncAzureOpenAI(
#         api_key = os.getenv("OPENAI_API_KEY"),
#         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
#         api_version = os.getenv("OPENAI_API_VERSION")
#     )

#     stream = await client.chat.completions.create(
#         model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
#         messages = [
#             {"role":"system","content":"You are a helpful assistant."},
#             {"role":"user","content":"Please write a poem of 500 words that relates to the theme of nature."}
#         ],
#         stream = True
#     )

#     async for chunk in stream:
#         if chunk.choices and chunk.choices[0].delta:
#             pprint(chunk.choices[0].delta.content or "", end="")

# if __name__ == "__main__":
#     load_dotenv()
#     asyncio.run(main())

def main():

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    response = openai.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages = [
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":"Please write a poem of 500 words that relates to the theme of nature."}
        ],
        stream = True
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            pprint(chunk.choices[0].delta.content or "", end="")

if __name__ == "__main__":
    load_dotenv()
    main()
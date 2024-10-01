from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from rich import print as pprint
import os
import asyncio

async def main():

    client = AsyncAzureOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version = os.getenv("OPENAI_API_VERSION"),
    )

    message = [
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":"What is the highest mountain in the world?"}
    ]

    stream = await client.chat.completions.create(
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages = message,
        stream = True
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta:
            pprint(chunk.choices[0].delta.content or "", end="")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
import os,json,sys
from dotenv import load_dotenv
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

def main():

    key = os.getenv("AZURE_TRANSLATOR_KEY")
    endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
    region = os.getenv("AZURE_TRANSLATOR_REGION")
    credential = AzureKeyCredential(key)

    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential, region=region)

    try:

        input_text_elements = [InputTextItem(text="我是一名工程師")]
        target_langauge = ["ja","en"]

        response = text_translator.translate(body=input_text_elements, to_language=target_langauge)

        translation = response[0] if response else None
        print("Detected Language: ", translation["detectedLanguage"].language)
        print(translation)

    except HttpResponseError as exception:
        print(f"Error Code:{exception.error.code}")
        print(f"Message:{exception.error.message}")

if __name__ == "__main__":
    load_dotenv()
    main()


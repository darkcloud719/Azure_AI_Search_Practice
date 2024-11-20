import os,json,sys,typing
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def main():

    key = os.getenv("AZURE_LANGUAGE_KEY")
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    region = os.getenv("AZURE_LANGUAGE_REGION")

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key), region=region)
    reviews = [
    """I am Nick Chang.I work for Foo Company, and we hired Contoso for our annual founding ceremony. The food
    was amazing and we all can't say enough good words about the quality and the level of service.""",
    """We at the Foo Company re-hired Contoso after all of our past successes with the company.
    Though the food was still great, I feel there has been a quality drop since their last time
    catering for us. Is anyone else running into the same problem?""",
    """Bar Company is over the moon about the service we received from Contoso, the best sliders ever!!!!"""
    ]

    result = text_analytics_client.recognize_entities(reviews)
    result = [review for review in result if not review.is_error]
    organization_to_reviews: typing.Dict[str,typing.List[str]] = {}

    for idx, review in enumerate(result):
        for entity in review.entities:
            print(f"Entity '{entity.text}' has category '{entity.category}'")
    print(result)

if __name__ == "__main__":
    load_dotenv()
    main()
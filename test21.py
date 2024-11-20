import os,json,sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def main():

    key = os.getenv("AZURE_LANGUAGE_KEY")
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    region = os.getenv("AZURE_LANGUAGE_REGION")

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key), region=region)

    documents = ["My life is tough."]

    result = text_analytics_client.analyze_sentiment(documents=documents, show_opinion_mining=True)
    docs = [doc for doc in result if not doc.is_error]

    print("Let's visualize the sentiment of each of these documents")
    for idx, doc in enumerate(docs):
        print(f"Document text: {documents[idx]}")
        print(f"Overall sentiment: {doc.sentiment}")
        print(f"Positive score: {doc.confidence_scores.positive}")
        print(f"Neutral score: {doc.confidence_scores.neutral}")
        print(f"Negative score: {doc.confidence_scores.negative}")

    print(result)

if __name__ == "__main__":
    load_dotenv()
    main()
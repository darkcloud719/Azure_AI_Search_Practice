import os 
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
def main():

    endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
    key = os.getenv("AZURE_COMPUTER_VISION_KEY")

    assert endpoint, "Missing environment variable 'AZURE_COMPUTER_VISION_ENDPOINT'"
    assert key, "Missing environment variable 'AZURE_COMPUTER_VISION_KEY'"

    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    with open("cat2.jpg","rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.CAPTION],
    )

    print("Image analysis results:")
    print("Caption:")
    if result.caption is not None:
        print(f"    '{result.caption.text}', Confidence {result.caption.confidence:.4f}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")

if __name__ == "__main__":
    load_dotenv()
    main()
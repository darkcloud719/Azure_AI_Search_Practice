import os 
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

def main():

    try:
        endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
        key = os.getenv("AZURE_COMPUTER_VISION_KEY")
    except KeyError:
        print("Missing environment variable 'AZURE_COMPUTER_VISION_ENDPOINT' or 'AZURE_COMPUTER_VISION_KEY'")
        print("Set them before running this sample")
        exit()

    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    result = client.analyze_from_url(
        image_url="https://learn.microsoft.com/azure/ai-services/computer-vision/media/quickstarts/presentation.png",
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ]
    )

    print("Image analysis results:")

    print(" Caption:")
    if result.caption is not None:
        print(f"    '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

    print(" Read:")
    if result.read is not None:
        for line in result.read.blocks[0].lines:
            print(f"    Line: '{line.text}', Bounding box {line.bounding_polygon}")
            for word in line.words:
                print(f"    Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

if __name__ == "__main__":
    load_dotenv()
    main()


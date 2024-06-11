import os
import sys
import requests
from PIL.Image import Resampling
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


def main() -> None:
    global cv_client

    try:
        load_dotenv()
        cs_endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
        cs_key = os.getenv('AZURE_COMPUTER_VISION_KEY')
        openai_key = os.getenv("OPEN_AI_KEY")

        # Get image
        image_file = 'images/street.jpg'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Load image to analyze into a 'bytes' object
        with open(image_file, "rb") as f:
            image_data = f.read()

        # Authenticate Azure AI Vision client
        cv_client = ImageAnalysisClient(
            endpoint=cs_endpoint,
            credential=AzureKeyCredential(cs_key)
        )

        # Background removal
        background_foreground(cs_endpoint, cs_key, image_data)
    except Exception as ex:
        print(ex)



def background_foreground(endpoint: str, key: str, image_data: bytes):
    # Define the API version and mode
    api_version = "2023-02-01-preview"
    mode = "backgroundRemoval"  # Can be "foregroundMatting" or "backgroundRemoval"

    # Remove the background from the image or generate a foreground matte
    print('\nRemoving background from image...')

    url = "{}computervision/imageanalysis:segment?api-version={}&mode={}".format(endpoint, api_version, mode)
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(url, headers=headers, data=image_data)
    image = response.content

    with open("images/backgroundForeground.png", "wb") as file:
        file.write(image)
    print('  Results saved in images/backgroundForeground.png \n')



if __name__ == '__main__':
    main()

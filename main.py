import base64
import io
import os
import sys

import cv2
import requests
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    try:
        load_dotenv()
        cs_endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
        cs_key = os.getenv('AZURE_COMPUTER_VISION_KEY')
        openai_key = os.getenv("OPEN_AI_KEY")

        # Get image
        image_file = 'images/person.jpg'

        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Obtain target size of the generated image using the original image dimensions
        size = get_target_image_size(image_path=image_file)

        # Generate a thumbnail with smart cropping for a subject-focused image
        thumbnail = save_smart_thumbnail(endpoint=cs_endpoint,
                                          key=cs_key,
                                          image_file=image_file,
                                          image_size=size
                                          )

        # Create an inverted image matte to show the focus areas for OpenAI the Image Edit API
        masked_image = process_image_matte(cs_endpoint, cs_key, thumbnail)

        # Connect to OpenAI Image Edit API
        client = OpenAI(api_key=openai_key)

        generated_image_size = generate_image_size_literal(size)

        print('Generating image...')
        response = client.images.edit(
            image=open(thumbnail, "rb"),
            mask=open(masked_image, "rb"),
            prompt="A super hero in the style of an american comic",
            n=1,
            response_format="b64_json",
            size=generated_image_size
        )
        print('Images have been generated')
        save_generated_images(response)
    except Exception as ex:
        print(ex)


def process_image_matte(cs_endpoint, cs_key, thumbnail):
    matted_image = grayscale_image(cs_endpoint, cs_key, thumbnail)
    matted_image = cv2.imread(matted_image, cv2.IMREAD_GRAYSCALE)
    inverted_image = cv2.bitwise_not(matted_image)
    inverted_image_path = 'images/invertedBackgroundForeground.png'
    cv2.imwrite(inverted_image_path, inverted_image)
    # Make the matted image transparent to allow editing on image focus
    masked_image = transparentize_grayscale_image(inverted_image_path)
    return masked_image


def save_generated_images(response):
    index = 1
    for data in response.data:
        generated_image_b64_encoding = data.b64_json
        image_data = base64.b64decode(generated_image_b64_encoding)
        generated_image_path = f'images/generated/generated{index}.png'
        # Save the image data to a file
        with open(generated_image_path, 'wb') as image_file:
            image_file.write(image_data)
            print(f'Results saved in {generated_image_path}')
        index += 1


def generate_image_size_literal(size):
    size_map = {
        256: "256x256",
        512: "512x512",
        1024: "1024x1024"
    }
    return size_map.get(size)


def grayscale_image(endpoint: str, key: str, image_file: str) -> str:
    # Load image to analyze into a 'bytes' object
    with open(image_file, "rb") as f:
        image_data = f.read()

    output_path = "images/backgroundForeground.png"
    # Define the API version and mode
    api_version = "2023-02-01-preview"
    mode = "foregroundMatting"  # Can be "foregroundMatting" or "backgroundRemoval"
    url = "{}computervision/imageanalysis:segment?api-version={}&mode={}".format(endpoint, api_version, mode)

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(url, headers=headers, data=image_data)
    image = response.content

    with open(output_path, "wb") as file:
        file.write(image)

    print(f'Results saved in {output_path}\n')

    return output_path


def save_smart_thumbnail(endpoint: str, key: str, image_file: str, image_size: int) -> str:
    # Load image to analyze into a 'bytes' object
    with open(image_file, "rb") as f:
        image_data = f.read()

    output_path = "images/smartCropped.png"
    url = "{}vision/v3.2/generateThumbnail?overload=stream&width={}&height={}".format(endpoint, image_size, image_size)
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }

    print('Generating thumbnail with smart cropping...\n')
    response = requests.post(url=url, headers=headers, data=image_data)
    image = response.content

    with Image.open(io.BytesIO(image)) as file:
        file.save(output_path, format='PNG')
    print(f'Results saved in {output_path}\n')

    return output_path


# Process a grayscale image so that the black areas are semi-transparent
def transparentize_grayscale_image(image_path: str) -> str:
    with Image.open(image_path) as f:
        if f.mode != 'L':
            f = f.convert('L')
            # Convert to 'RGBA' mode
        image_rgba = f.convert('RGBA')
        image_data = image_rgba.getdata()

    # Apply the alpha adjustment
    new_image_data = [adjust_alpha(pixel) for pixel in image_data]

    # Update the image data
    image_rgba.putdata(new_image_data)

    # Save the resulting image
    output_path = 'images/mask.png'
    image_rgba.save(output_path)

    print(f"Image saved to {output_path}")
    return output_path


# Define a function to adjust the alpha (transparency) based on the grayscale value
def adjust_alpha(pixel):
    # The original image is grayscale, so R, G, B will be the same
    # Extract the grayscale value (0 to 255)
    grayscale_value = pixel[0]
    # White (255) should be fully opaque, black (0) should be more transparent
    alpha = grayscale_value
    # Keep the white areas fully opaque and make black areas more transparent
    # For example, here white stays white, and black becomes semi-transparent
    return (255, 255, 255, 255) if grayscale_value == 255 else (0, 0, 0, alpha)


"""
Generate a target size for the user uploaded image based on the original size.
The target size represents the width and height for a new square image.
"""
def get_target_image_size(image_path):
    # Open the image
    with Image.open(image_path) as img:
        # Get original dimensions
        width, height = img.size

        # Determine the target size
        if width >= 1024 or height >= 1024:
            target_size = 1024
        elif width >= 512 or height >= 512:
            target_size = 512
        else:
            target_size = 256

        print(f"Resized image size: {target_size}x{target_size}\n")
        return target_size


if __name__ == '__main__':
    main()

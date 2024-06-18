import base64
import io
import os

import cv2
import requests
from PIL import Image
from dotenv import load_dotenv


def edit_image(client, mode, prompt, image_path):
    try:
        load_dotenv()
        cs_endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
        cs_key = os.getenv('AZURE_COMPUTER_VISION_KEY')

        # Obtain target size of the generated image using the original image dimensions
        size = get_target_image_size(image_path=image_path)

        # Generate a thumbnail with smart cropping for a subject-focused image
        thumbnail = save_smart_thumbnail(endpoint=cs_endpoint,
                                         key=cs_key,
                                         image_file=image_path,
                                         image_size=size
                                         )

        if mode == "foregroundMatting":
            # Create a masked version of the image to show the focus areas for OpenAI the Image Edit API
            masked_image = process_image_matte(cs_endpoint, cs_key, thumbnail)
        else:
            masked_image = background_foreground(cs_endpoint, cs_key, "backgroundRemoval", thumbnail)

        generated_image_size = generate_image_size_literal(size)

        print('Editing image...')
        response = client.images.edit(
            image=open(thumbnail, "rb"),
            mask=open(masked_image, "rb"),
            prompt=prompt,
            n=1,
            response_format="b64_json",
            size=generated_image_size
        )
        print('Images have been edited')
        save_generated_images(response)
    except Exception as e:
        print(e)


# Process a grayscale image so that the black areas are semi-transparent
def process_image_matte(cs_endpoint, cs_key, thumbnail):
    matted_image = background_foreground(cs_endpoint, cs_key, "foregroundMatting", thumbnail)
    matted_image = cv2.imread(matted_image, cv2.IMREAD_GRAYSCALE)
    inverted_image = cv2.bitwise_not(matted_image)
    inverted_image_path = os.path.join(os.curdir, "images", "invertedBackgroundForeground.png")
    cv2.imwrite(inverted_image_path, inverted_image)
    # Make the matted image transparent to allow editing on image focus
    masked_image = transparentize_image_matte(inverted_image_path)
    return masked_image


def save_generated_images(response):
    index = 1
    for data in response.data:
        generated_image_b64_encoding = data.b64_json
        image_data = base64.b64decode(generated_image_b64_encoding)
        image_dir = os.path.join(os.curdir, 'images', 'edits')
        image_path = os.path.join(image_dir, f'edit{index}.png')
        # Save the image data to a file
        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)
            print(f'Results saved in {image_path}')
        index += 1


def generate_image_size_literal(size):
    size_map = {
        256: "256x256",
        512: "512x512",
        1024: "1024x1024"
    }
    return size_map.get(size)


def background_foreground(endpoint: str, key: str, mode: str, image_file: str) -> str:
    # Load image to analyze into a 'bytes' object
    with open(image_file, "rb") as f:
        image_data = f.read()

    output_path = os.path.join(os.curdir, 'images', 'backgroundForeground.png')
    # Define the API version and mode
    api_version = "2023-02-01-preview"
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

    output_path = os.path.join(os.curdir, 'images', 'smartCropped.png')
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


def transparentize_image_matte(image_path: str) -> str:
    print('Transparentizing focus area...\n')
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
    output_path = os.path.join(os.curdir, 'images', 'mask.png')
    image_rgba.save(output_path)

    print(f"Image saved to {output_path}\n")
    return output_path


# Adjust the alpha (transparency) based on the grayscale value
def adjust_alpha(pixel):
    grayscale_value = pixel[0]
    alpha = grayscale_value
    return (255, 255, 255, 255) if grayscale_value == 255 else (0, 0, 0, alpha)


# Generate a target size for the user uploaded image based on the original size
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

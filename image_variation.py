import base64
import os
from PIL import Image
from openai import OpenAI


def create_variation(client: OpenAI, image_path: str):
    try:
        initialize_variant_directory()
        # Obtain target size of the generated image using the original image dimensions
        size = get_target_image_size(image_path=image_path)

        generated_image_size = generate_image_size_literal(size)
        save_image_as_png(image_path)
        print('Creating image variants...')
        response = client.images.create_variation(
            image=open(image_path, "rb"),
            n=4,
            response_format="b64_json",
            size=generated_image_size
        )
        print('Images variants have been created')
        save_image_variants(response)
    except Exception as e:
        print(e)


def initialize_variant_directory():
    image_dir = os.path.join(os.curdir, 'images', 'variants')
    # If the directory doesn't exist, create it
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)


def save_image_as_png(input_path: str) -> str:
    try:
        # Open the JPG image
        jpg_image = Image.open(input_path)

        # Save the image as a PNG file
        jpg_image.save(input_path, "PNG")
        print(f"\nImage successfully converted to PNG")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_image_variants(response):
    index = 1
    for data in response.data:
        generated_image_b64_encoding = data.b64_json
        image_data = base64.b64decode(generated_image_b64_encoding)
        image_dir = os.path.join(os.curdir, 'images', 'variants')
        image_path = os.path.join(image_dir, f'variant{index}.png')
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

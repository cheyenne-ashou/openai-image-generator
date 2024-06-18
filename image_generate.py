import base64
import os

from openai.lib.azure import AzureOpenAI


def generate_image(client: AzureOpenAI, prompt: str):
    try:
        # Define the parameters for image generation
        response = client.images.generate(
            model="image-generation",  # the name of your DALL-E 3 deployment
            prompt=prompt,
            response_format="b64_json",
            n=1
        )
        save_generated_images(response)
    except Exception as e:
        print(e)


def save_generated_images(response):
    index = 1
    for data in response.data:
        generated_image_b64_encoding = data.b64_json
        image_data = base64.b64decode(generated_image_b64_encoding)
        image_dir = os.path.join(os.curdir, 'images', 'generated',)
        image_path = os.path.join(image_dir, f'generated{index}.png')
        # Save the image data to a file
        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)
            print(f'Results saved in {image_path}')
        index += 1

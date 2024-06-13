import argparse
import os

from PIL import Image
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai import OpenAI

import image_edit
import image_generate


def main() -> None:
    # Set up command line argument parsing
    parser = get_parser()

    # Set the directory for the stored image
    initialize_image_directory()

    args = parser.parse_args()
    prompt = args.prompt

    # Validate 'edit' version arguments and edit image
    if args.v == "edit":
        edit_images(parser, args, prompt)
    elif args.v == "generate":
        print("Image generation is not yet supported")
        return
        api_version = "2024-02-01"
        client = establish_azure_openai_connection(api_version=api_version)
        image_generate.generate_image(client)
    else:
        return


def edit_images(parser, args, prompt: str):
    if not args.image_path:
        parser.error("--base_image is required when version is 'edit'")
        return
    if not args.mode:
        parser.error("--mode is required when version is 'edit'")
        return
    if args.mode == "background":
        mode = "backgroundRemoval"
    elif args.mode == "foreground":
        mode = "foregroundMatting"
    else:
        parser.error("--mode must be 'background' or 'foreground' (without quotations)")
        return

    image_path = args.image_path
    client = establish_openai_connection()
    image_edit.edit_image(client=client, mode=mode, prompt=prompt, image_path=image_path)

    save_original_image(image_path)


def initialize_image_directory():
    image_dir = os.path.join(os.curdir, 'images')
    # If the directory doesn't exist, create it
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)


def get_parser():
    parser = argparse.ArgumentParser(description="Azure OpenAI DALL-E Image API")
    parser.add_argument("--v", type=str, required=True, choices=["generate", "edit"],
                        help="API version: 'generate' or 'edit'")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt for DALL-E to generate or edit the image")
    parser.add_argument("--image_path", type=str, required=False, help="Path to the base image file")
    parser.add_argument("--mode",
                        type=str,
                        required=False,
                        help="Defines which part of the image to edit (only for image editing).",
                        choices=["background", "foreground"])
    return parser


def save_original_image(image_path):
    print(f"Saving original image...\n")
    with Image.open(image_path) as img:
        # Define the new file path
        new_path = os.path.join(os.curdir, 'images', 'original.png')
        # Save the image to the new path
        img.save(new_path)
        print(f"Image saved to {new_path}")


def establish_azure_openai_connection(api_version: str) -> AzureOpenAI:
    load_dotenv()
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    client = AzureOpenAI(api_version=api_version, api_key=api_key, azure_endpoint=azure_endpoint)
    return client


def establish_openai_connection() -> OpenAI:
    # Connect to OpenAI Image Edit API
    load_dotenv()
    openai_key = os.getenv("OPEN_AI_KEY")
    client = OpenAI(api_key=openai_key)
    return client


if __name__ == '__main__':
    main()

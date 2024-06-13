import os


def generate_image(client):
    # Set the directory for the stored image
    image_dir = os.path.join(os.curdir, 'images')

    # Initialize the image path (note the filetype should be png)
    image_path = os.path.join(image_dir, 'generated_image.png')

    # Define the parameters for image generation
    response = client.Image.create(
        prompt="A beautiful sunset over a mountain range",
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print("Generated Image URL:", image_url)

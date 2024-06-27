### AI Image Playground
## Overview
This project allows users to generate, edit, and create variant images using user prompts.
It uses Azure Cognitive Services and Open AI's Dall-E image models.
My goal for this project is to learn more about what AI has to offer.
To see what this project has to offer, please use it for yourself!

## Try it out

**Env File**

Create a .env file at the root of the project and copy and paste the contents of .env-example into the .env file.

For the image edit functionality, you will need to create an Azure Computer Vision instance and make in account through the OpenAI website where you can obtain an api key.

For the image generation functionality, you will need an Azure Open AI Account.

**Clone the repository**

Using the command line, navigate to the folder you would like to keep the project, then clone the repo.
```commandline
foo@bar:~$ git clone https://github.com/cheyenne-ashou/openai-phishing-detection.git
```

**Install Dependencies**


```commandline
foo@bar:~$ pip install openai
foo@bar:~$ pip install python-dotenv
foo@bar:~$ pip install opencv-python
foo@bar:~$ pip install requests
foo@bar:~$ pip install pillow 
```

**Usage**

For usage instructions, simply navigate to the openai-image-generator folder and the following command will show you how it should be used:
```commandline
foo@bar:./openai-image-generator$ python main.py -h 
```
To use the image edit capability, you must get the filepath of your image. For example:
```commandline
foo@bar:~$ python main.py --v edit --prompt "Super hero Iron man" --image_path "images/person.jpg" --mode foreground
```

**Results**

Original Image:

![person](https://github.com/cheyenne-ashou/openai-image-generator/assets/54869764/7ce7c638-4b2c-4e36-bc6f-ca474bc70201)

Generated Image:

![image](https://github.com/cheyenne-ashou/openai-image-generator/assets/54869764/3fb9be65-37ce-4016-abd6-f55c33b30e3c)

## Technology
1. Azure Cognitive Services - Computer Vision
   - Thumbnail / Smart Cropping API
     - Generate a thumbnail with focus on the primary subject of the image. This allows us to create a standardized square image where we can further process it for our use-case.
   - Image Analysis - Segment API
     - Separate the image stream into segments, allowing for separation between the background and foreground. The returned image is used to help identify the background and foreground, which is then used to create an image edit using Open AI.
2. OpenAI
   - Image Edit API
     - Edit a specified area of an image by providing a mask of the foreground or background
   - Image Generation API
     - Generate an image based on user prompt
   - Image Variant API
     - Generate variant images based on an inputed image.
## Plans for the future
As this project's primary goal is to learn about AI, I plan on incorporating more AI technologies as I learn more.
In addition to this, I would like to build a web interface using Django to allow for easy interaction with all the capabilities of this project.

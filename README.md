### AI Image Playground
## Overview
This project aims to allow users to create and edit images.
It uses Azure Cognitive Services and Open AI's Dall-E image models.
My goal for this project is to learn more about what AI has to offer.
To see what this project has to offer, please use it for yourself!

## Try it out
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

![img_1.png](img_1.png)
Generated Image:

![img.png](img.png)
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
## Plans for the future
As this project's primary goal is to learn about AI, I plan on incorporating more AI technologies as I learn more.
In addition to this, I would like to build a web interface using Django to allow for easy interaction with all the capabilities of this project.
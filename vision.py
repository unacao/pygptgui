from openai import OpenAI
import pyautogui
import os
import base64
import requests
import subprocess

# Path to your image
TEMP_SCREENSHOT_PATH = "temp.png"

api_key = os.environ.get('OPENAI_API_KEY')

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def take_screenshot(image_path=TEMP_SCREENSHOT_PATH):
    # Take a screenshot
    screenshot = pyautogui.screenshot()
    scale = 4
    downsampled_image = screenshot.resize(
        (screenshot.width // scale, screenshot.height // scale))

    print(downsampled_image)
    screen_size = screenshot.size
    print(screen_size)

    # Save the screenshot as "temp.jpg" in the current directory
    downsampled_image.save(image_path)
    return downsampled_image, screen_size

def is_retina():
    return subprocess.call("system_profiler SPDisplaysDataType | grep 'Retina'", shell= True) == 0

def crop_image(image, xmin, ymin, xmax, ymax):
    # Get the width and height of the image
    width, height = image.size

    # Calculate the pixel coordinates
    xmin_pixel = int(xmin * width)
    ymin_pixel = int(ymin * height)
    xmax_pixel = int(xmax * width)
    ymax_pixel = int(ymax * height)

    # Crop the image
    cropped_image = image.crop((xmin_pixel, ymin_pixel, xmax_pixel, ymax_pixel))
    return cropped_image

def move_to_block(x, y, xmin, ymin, xmax, ymax):
    x = xmin + (xmax - xmin) * x
    y = ymin + (ymax - ymin) * y
    xcenter = (xmin + xmax) / 2.0
    ycenter = (ymin + ymax) / 2.0
    crop_xmin, crop_ymin, crop_xmax, crop_ymax = 0, 0, 1, 1
    if x < xcenter:
        crop_xmax = 0.5
    else:
        crop_xmin = 0.5

    if y < ycenter:
        crop_ymax = 0.5
    else:
        crop_ymin = 0.5

    print(f"moving mouse to ({x}, {y})")
    pyautogui.moveTo(x, y, 1, pyautogui.easeOutQuad)
    return crop_xmin, crop_ymin, crop_xmax, crop_ymax

def ask(concept: str):
    image_path = TEMP_SCREENSHOT_PATH
    screen, screen_size = take_screenshot(image_path=image_path)
    width, height = screen_size
    if is_retina():
        width /= 2
        height /= 2
    screen_xmin = 0
    screen_ymin = 0
    screen_xmax = width
    screen_ymax = height

    for _ in range(3):
        # Sequential localization.
        query = f"Where is `{concept}`? Share the x_min, y_min, x_max, y_max in 0-1 normalized space. Only return the numbers, nothing else."
        response = ask_gpt(query, image_path=image_path)
        message = response['choices'][0]['message']
        role = message['role']
        content = message['content']
        xmin, ymin, xmax, ymax = tuple(map(float, content.split(',')))
        x = (xmin+xmax) / 2.0
        y = (ymin+ymax) / 2.0
        crop_xmin, crop_ymin, crop_xmax, crop_ymax = move_to_block(x, y, screen_xmin, screen_ymin, screen_xmax, screen_ymax)

        # Refine the bbox.
        screen = crop_image(screen, crop_xmin, crop_ymin, crop_xmax, crop_ymax)
        screen.save(image_path)
        new_xmin = screen_xmin + crop_xmin * (screen_xmax - screen_xmin)
        new_xmax = screen_xmin + crop_xmax * (screen_xmax - screen_xmin)
        new_ymin = screen_ymin + crop_ymin * (screen_ymax - screen_ymin)
        new_ymax = screen_ymin + crop_ymax * (screen_ymax - screen_ymin)
        screen_xmin, screen_xmax, screen_ymin, screen_ymax = new_xmin, new_xmax, new_ymin, new_ymax

    pyautogui.click()

    return response


def ask_gpt(query: str, image_path=TEMP_SCREENSHOT_PATH):

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model":
        "gpt-4-vision-preview",
        "messages": [{
            "role":
            "user",
            "content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }],
        "max_tokens":
        300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions",
                             headers=headers,
                             json=payload)

    return response.json()



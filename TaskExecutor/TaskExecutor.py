import os
import time
import json
import pyautogui
from PIL import ImageGrab
import webbrowser
import requests
import base64

from dotenv import load_dotenv
root_path = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(root_path,".env"))

OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
INPUT_FOLDER = os.getenv("INPUT_FOLDER")

class TaskExecutor:
    def __init__(self, SERVER_URL, API_KEY):
        self.server_url = SERVER_URL
        self.api_key = API_KEY
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(INPUT_FOLDER, exist_ok=True)  


    def take_screenshot(self, idx):
        # Take a screenshot
        screenshot_path = os.path.join(INPUT_FOLDER, f"screenshot_{idx}.png")
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        return screenshot_path
    
    def open_webpage(self):
        # Open the URL in the default browser
        url = input("Please enter a valid url: ")
        webbrowser.open(url)
        time.sleep(2)
        pyautogui.press('f11')
        time.sleep(2)

    def create_task(self):
        
        task_path = os.path.join(INPUT_FOLDER, "task.json")
        # Prompt for task input
        task_input = input("Please enter a task: ")
        json_task = {"task": task_input}

        # Save the JSON data to the file
        with open(task_path, "w") as file:
            json.dump(json_task, file, indent=4)

        # Wait for the file to be created with a timeout
        timeout = 2  # seconds
        start_time = time.time()
        while not os.path.exists(task_path):
            if time.time() - start_time > timeout:
                raise TimeoutError("File was not created within the timeout period.")
            time.sleep(0.1)

        print(f"Task saved to {task_path}")
        return task_input

    def perform_action(self, json_data):
        """
        Perform the action based on the extracted action and coordinates from the JSON.
        Currently, it supports 'click' actions.

        :param action: The action to be performed (e.g., 'click')
        :param coordinates: The coordinates where the action will be performed
        """
        action = json_data.get("ACTION")
        element = json_data.get("ELEMENT")
        details = json_data.get("DETAILS")
        coordinates = json_data.get("COORDINATES")

        if action == "click" and coordinates:
            # pyautogui click action at the specified coordinates
            x1, y1, x2, y2 = coordinates

            x = x1+(x2/2)
            y = y1+(y2/2)
            print(f"Clicking at ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(1)  # Adding a short delay to avoid too fast execution
            
        elif action == "type" and coordinates:
            x1, y1, x2, y2 = coordinates
            x = x1+(x2/2)
            y = y1+(y2/2)
            print(f"Clicking at ({x}, {y})")
            pyautogui.click(x, y)
            # If the action was 'type', you could use pyautogui to type at certain coordinates
            print(f"Typing at {coordinates}")
            pyautogui.write(details)  # Example text to type, can be modified
            pyautogui.press("enter")
        elif action == "wait":
            time.sleep(5)
        else:
            print("Unsupported action or missing coordinates!")

    def request(self, image_path, task_description):
        """
        Send an image and task description to the TaskBuilder API.
        
        Args:
            image_path (str): Path to the image file
            task_description (str): Description of the task to perform
        
        Returns:
            dict: API response containing result file paths
        """
        # Prepare the files and data for multipart upload
        with open(image_path, 'rb') as image_file:
            files = {
                'file': (os.path.basename(image_path), image_file, 'image/png'),
                'task': (None, task_description)
            }
            
            
            if self.server_url != 'http://localhost:8000':
                # Send POST request to the build endpoint
                headers = {'Authorization': f'Bearer {self.api_key}'}
                response = requests.post(
                    f"{self.server_url}/build/",
                    files=files,
                    headers=headers
                )
            else:
                # Send POST request to the build endpoint
                response = requests.post(
                    f"{self.server_url}/build/", 
                    files=files
                )
            
        # Check for successful response
        response.raise_for_status()
        
        return response.json()
    
    def save_result_files(self, api_response, idx):
        """
        Save the result files from the API response.
        
        Args:
            api_response (dict): Response from build_task method
            output_dir (str): Directory to save result files
        
        Returns:
            dict: Paths to saved result files
        """
        
    # Save JSON result
        json_result = api_response['result_json']
        json_path = os.path.join(OUTPUT_FOLDER, f'result_{idx}.json')
        with open(json_path, 'w') as f:  # Use 'w' for writing text
            json.dump(json_result, f, indent=4)  # Write the JSON data directly
        
        # Save result image
        image_result = api_response['result_image']
        image_path = os.path.join(OUTPUT_FOLDER, f'labled_screenshot_{idx}.png')
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_result))  # Decode and write the image data

        
        return json_result

from TaskBuilder.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from ultralytics import YOLO
from PIL import Image
import io
import base64
import os
from anthropic import Anthropic
import json

# Load environment variables from .env file
from dotenv import load_dotenv
root_path = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(root_path,".env"))

INPUT_FOLDER = os.getenv("INPUT_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH")
CAPTION_MODEL_NAME = os.getenv("CAPTION_MODEL_NAME")
CAPTION_MODEL_PATH = os.getenv("CAPTION_MODEL_PATH")


class TaskBuilder:

    def __init__(self, device):
        """
        Initialize the IconDetector with specified models and device.

        Args:
            device (str): Computation device ('cuda' or 'cpu')
            yolo_model_path (str): Path to YOLO model weights
            caption_model_name (str): Name of caption model (e.g., 'blip2', 'florence2')
            caption_model_path (str): Path to caption model weights
        """



        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(INPUT_FOLDER, exist_ok=True)

        self.device = device
        self.LLM = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.som_model, self.caption_model_processor = self.initialize_models(
            yolo_model_path = YOLO_MODEL_PATH, 
            caption_model_name = CAPTION_MODEL_NAME, 
            caption_model_path = CAPTION_MODEL_PATH)
        

    def initialize_models(self, 
        yolo_model_path,
        caption_model_name,
        caption_model_path):
        """
        Initialize YOLO and caption models.
        
        Args:
            yolo_model_path (str): Path to YOLO model weights
            caption_model_name (str): Name of caption model
            caption_model_path (str): Path to caption model weights
        """
        
        # Initialize YOLO model
        som_model = get_yolo_model(model_path=yolo_model_path)
        som_model.to(self.device)
        print(f'Model moved to {self.device}')
        
        # Initialize caption model
        caption_model_processor = get_caption_model_processor(
            model_name=caption_model_name,
            model_name_or_path=caption_model_path,
            device=self.device
        )
       

        return som_model, caption_model_processor

    def input(self, image):
        # Save the uploaded image
        image_path = os.path.join(INPUT_FOLDER, f"screenshot.png")
        with open(image_path, "wb") as buffer:
            buffer.write(image)
        return image_path

    def process_image(self, image_path, box_threshold=0.03):
        """
        Process an image and return labeled results.
        
        Args:
            image_path (str): Path to the input image
            box_threshold (float): Threshold for bounding box detection
        
        Returns:
            tuple: Labeled image, label coordinates, and parsed content list
        """
        
        # Open and convert image
        image = Image.open(image_path)
        image_rgb = image.convert('RGB')
        
        # Perform OCR
        ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
            image_path,
            display_img=False,
            output_bb_format='xyxy',
            goal_filtering=None,
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},
            use_paddleocr=True
        )
        text, ocr_bbox = ocr_bbox_rslt

        draw_bbox_config = {
            'text_scale': 0.8,
            'text_thickness': 2,
            'text_padding': 3,
            'thickness': 3,
        }
        
        # Get labeled image and results
        dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
            image_path,
            self.som_model,
            BOX_TRESHOLD=box_threshold,
            output_coord_in_ratio=False,
            ocr_bbox=ocr_bbox,
            draw_bbox_config=draw_bbox_config,
            caption_model_processor=self.caption_model_processor,
            ocr_text=text,
            use_local_semantics=True,
            iou_threshold=0.1
        )
        
        return dino_labled_img, label_coordinates, parsed_content_list

    def create_system_prompt(self):
        return """You are a task analyzer for a computer automation system. When given a task and a list of screen elements, you should:
                    1. Analyze the available screen elements
                    2. Return one instruction in this exact format for the specific step to execute:
                    {
                        "ACTION": "[click/type/wait]",
                        "ELEMENT": "\"Text Box/Icon Box ID X: [exact element text]\"",
                        "DETAILS": "[text to type or additional info if needed]"
                    }

                    Rules:
                    - You have the obligation to start with the instruction before saying anything else
                    - Only reference elements that exactly match the provided list
                    - Always include the full element ID and text in your reference
                    - Be specific about whether to click or type
                    - If typing is needed, specify the exact text to type
                    - Keep responses focused only on achievable actions with the given elements"""

    def analyze_task(self, task, screen_elements):
        screen_content = "\n".join(screen_elements)

        message = self.LLM.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Task to complete: {task}

                    Available screen elements:
                    {screen_content}

                    Provide step-by-step instructions using only the available elements. Format each step as specified in your system prompt."""
                }
            ],
            system=self.create_system_prompt()
        )

        return message.content
    
    def run(self, image_path, task):

        # Process the image
        dino_labled_img, label_coordinates, screen_elements = self.process_image(image_path)
        result_image_path = os.path.join(OUTPUT_FOLDER, f"labled_screenshot.png")
        Image.open(io.BytesIO(base64.b64decode(dino_labled_img))).save(result_image_path)

        # Analyze the parsed image
        result = self.analyze_task(task, screen_elements)
        json_text = result[0].text.split('\n')[0:4]
        json_result = json.loads('\n'.join(json_text) + '\n}')
        json_result['COORDINATES'] = label_coordinates[json_result['ELEMENT'].split()[3][:-1]].tolist()
        
        # Define the file path where you want to save the result
        result_file_path = os.path.join(OUTPUT_FOLDER, f"result.json")
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        with open(result_file_path, 'w') as json_file:
            json.dump(json_result, json_file, indent=4)

        print(f"Result has been saved to {result_file_path}")
        return result_file_path, result_image_path

    


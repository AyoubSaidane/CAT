import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from TaskBuilder.TaskBuilder import TaskBuilder
import base64, json

# Initialize the device
device = torch.device('cuda') if torch.cuda.is_available() else 'cpu'

# Create global TaskBuilder instance
taskBuilder = TaskBuilder(device=device)

# Create FastAPI app
app = FastAPI(
    title="TaskBuilder API",
    description="API for image parsing",
    version="1.0.0"
)

@app.post("/build/")
async def build(
    file: UploadFile = File(...), 
    task: str = File(...)
):
    """
    Analyze a screenshot for a specific task.
    
    - Upload a screenshot image
    - Provide a task description
    - Returns task analysis results
    """
    try:
        
        # Save the uploaded image
        image_path = taskBuilder.input(await file.read())
        
        # Run task analysis
        result_file_path, result_image_path = taskBuilder.run(image_path, task)
        with open(result_image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        with open(result_file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Return results
        return {
            "result_json": json_data,
            "result_image": image_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "device": str(device),
        "models_loaded": True
    }
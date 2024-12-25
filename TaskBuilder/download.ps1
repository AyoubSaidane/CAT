# Base URL for downloading model files
$BaseUrl = "https://huggingface.co/microsoft/OmniParser/resolve/main"

# Define folder structure and create folders
$folders = @(
    "TaskBuilder/weights/icon_detect",
    "TaskBuilder/weights/icon_caption_florence"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# Define required files and their URLs
$modelFiles = @{
    "TaskBuilder/weights/icon_detect/model.safetensors"      = "$BaseUrl/icon_detect/model.safetensors"
    "TaskBuilder/weights/icon_detect/model.yaml"            = "$BaseUrl/icon_detect/model.yaml"
    "TaskBuilder/weights/icon_caption_florence/model.safetensors" = "$BaseUrl/icon_caption_florence/model.safetensors"
    "TaskBuilder/weights/icon_caption_florence/config.json" = "$BaseUrl/icon_caption_florence/config.json"
}

# Download each file into its specified directory
foreach ($filePath in $modelFiles.Keys) {
    $url = $modelFiles[$filePath]
    Invoke-WebRequest -Uri $url -OutFile $filePath
}

Write-Host "All required model and configuration files downloaded and organised."

# Run the conversion script if necessary files are present
if ((Test-Path "TaskBuilder/weights/icon_detect/model.safetensors") -and 
    (Test-Path "TaskBuilder/weights/icon_detect/model.yaml")) {
    python TaskBuilder/weights/convert_safetensor_to_pt.py
}

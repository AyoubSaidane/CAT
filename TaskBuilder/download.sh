#!/bin/bash

# Base URL for downloading model files
BASE_URL="https://huggingface.co/microsoft/OmniParser/resolve/main"

# Define folder structure and create folders
mkdir -p TaskBuilder/weights/icon_detect
mkdir -p TaskBuilder/weights/icon_caption_florence

# Declare an associative array of required files with paths
declare -A model_files=(
  ["TaskBuilder/weights/icon_detect/model.safetensors"]="$BASE_URL/icon_detect/model.safetensors"
  ["TaskBuilder/weights/icon_detect/model.yaml"]="$BASE_URL/icon_detect/model.yaml"
  ["TaskBuilder/weights/icon_caption_florence/model.safetensors"]="$BASE_URL/icon_caption_florence/model.safetensors"
  ["TaskBuilder/weights/icon_caption_florence/config.json"]="$BASE_URL/icon_caption_florence/config.json"
)

# Download each file into its specified directory
for file_path in "${!model_files[@]}"; do
  echo "Downloading ${model_files[$file_path]} to $file_path"
  wget -O "$file_path" "${model_files[$file_path]}"
  if [ $? -ne 0 ]; then
    echo "Error downloading ${model_files[$file_path]}"
    exit 1
  fi
done

echo "All required model and configuration files downloaded and organised."

# Run the conversion script if necessary files are present
if [ -f "TaskBuilder/weights/icon_detect/model.safetensors" ] && [ -f "TaskBuilder/weights/icon_detect/model.yaml" ]; then
  python TaskBuilder/weights/convert_safetensor_to_pt.py
  echo "Conversion to best.pt completed."
else
  echo "Error: Required files for conversion not found."
fi
# CAT (Computer Automated Tasks)

CAT is a system designed to automate computer interactions using advanced AI vision and natural language processing. The system operates in two parts: a GPU-powered server component (OmniParser) for AI processing, and a local component (LocalExecutor) for GUI automation.

## Software Prerequisites
Before starting this project you will need to install these tools:
1. [Conda](https://docs.anaconda.com/miniconda/install/#quick-command-line-install)
2. [Docker](https://docs.docker.com/get-started/get-docker/)

You can verify if Conda and Docker have been successfully installed:
```bash
conda --version
docker --version
```

You will also need to get a valid Anthropic API key via the [Anthropic Console](https://console.anthropic.com/)

## Installation

To properly set up the TaskExecutor, follow these steps:

1. Clone this repository to your local machine:
```bash
git clone https://github.com/AyoubSaidane/CAT.git
cd CAT
```

2. Create and activate a conda environment:
```bash
conda create -n TaskExecutor -y
conda activate TaskExecutor
```

3. Install all required dependencies for the TaskExecutor:
```bash
pip install -r TaskExecutor/requirements.txt
```

For the TaskBuilder script, you have two options: local execution or remote execution on a Cloud Computing Server. We recommend using a GPU-equipped machine for better performance and lower latency. For either option:

1. Download the model weights:
```bash
# For Linux
bash TaskBuilder/download.sh

# For Windows
./TaskBuilder/download.ps1
```

2. Set your Anthropic API key in the [.env](TaskBuilder/.env) file
3. Build the Docker image:
```bash
docker build -t taskbuilder:latest .
```

## Execution
To run CAT, you need to start the TaskBuilder server either locally or on a remote machine.

### Local Execution
1. In your first terminal, start a Docker container:
```bash
docker run -p 8000:8000 taskbuilder:latest
```
This will start a FastAPI server on localhost.

2. In a second terminal, run:
```bash
conda activate TaskExecutor
python client.py --local
```

3. Enter your task and initial webpage URL when prompted.

### Remote Execution
1. Push the TaskBuilder image to Docker Hub:
```bash
docker tag taskbuilder:latest YOUR_DOCKER_REPOSITORY/taskbuilder:latest
docker push YOUR_DOCKER_REPOSITORY/taskbuilder:latest
```

2. Deploy the server on your preferred Cloud Computing Service. For [Lightning.ai](https://lightning.ai/):
   - Set up your Lightning account
   - Follow the [deployment guide](https://lightning.ai/docs/overview/serve-models/Deployments)
   - Note the server URL and Authentication Bearer Token

3. On your local machine, run:
```bash
conda activate TaskExecutor
python client.py --remote "YOUR_SERVER_URL" "YOUR_AUTH_BEARER_TOKEN"
```

4. Enter your task and initial webpage URL when prompted.

## How It Works

1. TaskExecutor captures screen information and sends it to OmniParser
2. OmniParser processes the image using AI vision models
3. Natural language instructions are interpreted into computer actions
4. TaskExecutor executes the determined actions
5. The process repeats for continuous automation

## Acknowledgments

This project builds upon the [OmniParser](https://github.com/microsoft/OmniParser) framework by Microsoft. We thank the original authors for their groundbreaking work in computer vision and automation.
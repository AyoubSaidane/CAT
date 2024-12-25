FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies including Python and OpenCV dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgtk2.0-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Install Python requirements
RUN pip install --no-cache-dir --upgrade -r /app/TaskBuilder/requirements.txt


EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
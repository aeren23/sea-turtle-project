FROM python:3.10-slim

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them
COPY ai-service/requirements.txt ./ai-service/
RUN pip install --no-cache-dir -r ai-service/requirements.txt

# We also need ultralytics, albumentations, etc. that are not in ai-service/requirements.txt
# because they were probably installed globally in the dev environment.
# Let's ensure the core data science dependencies are installed.
RUN pip install --no-cache-dir \
    ultralytics \
    faiss-cpu \
    opencv-python-headless \
    torch torchvision \
    albumentations

# Copy ai-service code
COPY ai-service/ /app/ai-service/

# We need to run from within ai-service so local imports (like 'import id_generator') work
WORKDIR /app/ai-service

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

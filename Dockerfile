# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
# We use --no-cache-dir to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the entrypoint to the Python script
# This allows users to pass arguments directly to the container
ENTRYPOINT ["python", "main.py"]

# Usage Instructions:
#
# 1. Run the container (mounting your current directory to /data so the app can read/write files):
#    docker run --rm -v $(pwd):/data note-generator /data/your_document.pdf --output-dir /data/output
#
# 2. Supplying API Keys (if using OpenAI or Gemini):
#    docker run --rm -e OPENAI_API_KEY="your-key" -v $(pwd):/data note-generator /data/your_document.pdf --provider openai
#
# 3. Connecting to Local Ollama (from container to host):
#    # For Mac/Windows:
#    docker run --rm -e OLLAMA_HOST="http://host.docker.internal:11434" -v $(pwd):/data note-generator /data/your_document.pdf --provider ollama
#    # For Linux:
#    docker run --rm --net=host -v $(pwd):/data note-generator /data/your_document.pdf --provider ollama

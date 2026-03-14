# Jesinia

A generalized CLI application that accepts presentations, Word documents, PDFs, and Markdown files, and uses AI to distill them into structured Markdown notes.

It's designed with a plug-and-play architecture that supports multiple AI providers (Ollama, OpenAI, Gemini) and features advanced generation strategies (like Map-Reduce) for handling long-context documents efficiently.

## Features
- **Multi-format Support**: 
  - `PDF`: Renders pages to images for vision-based OCR.
  - `PPTX`: Extracts slide titles and body text sequentially.
  - `DOCX`: Extracts continuous text grouped in paragraph chunks.
  - `MD`: Parses logical sections based on thematic breaks (`---`), or uses the LLM to intelligently insert breaks.
- **Provider Agnostic**: Easily switch between local inference (Ollama) or managed APIs (OpenAI, Gemini).
- **Generation Strategies**:
  - `map-reduce`: Generates notes independently for chunks, synthesizes them in groups, and combines them for the final document.
  - `feed-forward`: Merges newly extracted context into an ongoing, progressively evolving notes document.
- **Centralized Config**: A `config.yaml` manages all model properties, API retry behaviors, and prompt templates in one place.
- **Dockerized**: Fully bundled for cross-system, containerized deployments.

## Installation

### Method 1: Python Virtual Environment
1. Ensure Python 3.10+ is installed.
2. Clone the repository and navigate to the project directory.
3. Set up and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Docker
You can run the application directly using the pre-built Docker image `voidwalker07/jesinia`:
```bash
docker pull voidwalker07/jesinia
```

## Setup & Configuration

### AI Providers
The AI provider can be selected using the `--provider` flag or by setting the default inside `config/config.yaml`.

- **Ollama**: (Default) Ensure the Ollama app is running locally (`http://localhost:11434`) and run `ollama pull gemma3` to fetch the default model.
- **OpenAI**: Export your API key before running: `export OPENAI_API_KEY="sk-..."`
- **Gemini**: Export your API key before running: `export GEMINI_API_KEY="AI..."`

### Global Configuration (`config.yaml`)
You can tweak the exact LLM prompt instructions, models for each provider (e.g. swap `gpt-4o` for `gpt-4-turbo`), API rate limit retry parameters, and the chunk sizes for map-reduce directly inside `config/config.yaml`.

## Usage

### Basic CLI usage
By default, the application runs the `map-reduce` strategy using the `ollama` provider and outputs everything to `{filename}_notes.md`.

*Note: The current version of the application only accepts a single file as input. Support for batch processing multiple files is planned for a future release.*

```bash
python main.py slide_deck.pptx
python main.py resume.pdf
```

### Passing a Transcript
You can also provide a transcript file alongside the main document using the `--transcript` flag (currently unused, but supported by the CLI for future extension):
```bash
python main.py presentation.pptx --transcript lecture_audio.txt
```

### Specifying a Strategy
```bash
python main.py documentation.pdf --strategy feed-forward
```

### Specifying an AI Provider
```bash
python main.py documentation.pdf --provider openai
```

### Controlling the Output
Save notes to a custom directory, or overwrite the default filename.
```bash
python main.py document.pdf --output-dir ./extracted_notes --output-file special_notes.md
```

### Usage with Docker

Using Docker requires mounting a local directory into the container so the app can read your files and write the generated notes. We recommend mounting your current directory (`$(pwd)`) to `/data` inside the container.

#### 1. Basic Note Generation
Generate notes for a single file using the default (Ollama) provider and the map-reduce strategy.
```bash
docker run --rm -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf
```
*Note: The generated notes will appear in your current directory as `your_document_notes.md`.*

#### 2. Specifying output locations
Save notes to a specific folder or overwrite the default filename.
```bash
docker run --rm -v $(pwd):/data voidwalker07/jesinia /data/document.pdf \
  --output-dir /data/extracted_notes \
  --output-file custom_notes.md
```

#### 3. Changing the AI Strategy
Use the feed-forward strategy instead of map-reduce to merge information sequentially.
```bash
docker run --rm -v $(pwd):/data voidwalker07/jesinia /data/document.pdf \
  --strategy feed-forward
```

#### 4. Using OpenAI or Gemini
To use managed services, you must pass your API keys into the container using the `-e` flag.
```bash
# Using OpenAI
docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider openai

# Using Google Gemini
docker run --rm -e GEMINI_API_KEY="$GEMINI_API_KEY" -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider gemini
```

#### 6. Connecting to a Local Ollama (Host Machine)
If you are running Ollama directly on your host machine (not in another container), the Docker container needs special network configuration to reach it.

**For Mac/Windows (Docker Desktop):**
Use `host.docker.internal` to point the container to your machine.
```bash
docker run --rm -e OLLAMA_HOST="http://host.docker.internal:11434" -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider ollama
```

**For Linux:**
Use the `--net=host` flag.
```bash
docker run --rm --net=host -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider ollama
```

#### 6. Hardware Acceleration (NVIDIA GPUs)
If you have an NVIDIA GPU, you can pass the `--gpus all` flag to the container to speed up local extraction workloads (note: this requires installing the [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit) on your host machine).
```bash
docker run --rm --gpus all -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf
```

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

```bash
python main.py slide_deck.pptx
python main.py resume.pdf annual_report.docx
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
To process files via Docker, you must mount a local directory containing your documents to the container using `-v`.
```bash
# General Docker Run (Output directory is mapped to the current host directory)
docker run --rm -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --output-dir /data/output

# Using OpenAI or Gemini (Passing ENV vars)
docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider openai

# Using Local Ollama (Mac/Windows Docker Networking to Host)
docker run --rm -e OLLAMA_HOST="http://host.docker.internal:11434" -v $(pwd):/data voidwalker07/jesinia /data/your_document.pdf --provider ollama
```

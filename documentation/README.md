# Video Caption Suite - Documentation

## Overview

Video Caption Suite is a professional-grade media captioning application that generates detailed text descriptions for **videos and images** using any OpenAI-compatible vision-language model server (e.g. llama.cpp). It features a modern web interface, real-time progress tracking, GPU resource monitoring, and a prompt library.

## Table of Contents

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, data flow, and component relationships |
| [API.md](./API.md) | Complete REST and WebSocket API reference |
| [FRONTEND.md](./FRONTEND.md) | Vue components, Pinia stores, and UI architecture |
| [CONFIGURATION.md](./CONFIGURATION.md) | All configuration options and settings |
| [DEVELOPMENT.md](./DEVELOPMENT.md) | Setup, building, testing, and contributing |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A running **llama.cpp server** (or any OpenAI-compatible server) serving a vision-language model
  - Example: `llama-server --model qwen2.5-vl-7b-q4_k_m.gguf --port 8080 --mmproj mmproj.gguf`
  - Any server that implements `POST /v1/chat/completions` with `image_url` content blocks works

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "Video Caption Suite"

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

**Option 1: Using start script**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
# Terminal 1: Backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access the application at `http://localhost:5173`

### First-time Setup

1. Open the **Model** settings tab
2. Enter your llama.cpp server URL (default: `http://localhost:8080`)
3. Click **Refresh** to discover available models
4. Select the model you want to use (or type its name manually)
5. Click **Load Model** to verify connectivity
6. Set your working directory in the **Directory** tab

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, OpenAI SDK |
| Frontend | Vue 3, TypeScript, Pinia, Tailwind CSS, Vite |
| Inference | llama.cpp (or any OpenAI-compatible server) |
| Video Processing | OpenCV, Pillow |
| Communication | REST API + WebSocket |

## Key Features

- **Video & Image Captioning**: Generate detailed descriptions for both videos and images
- **OpenAI-Compatible API**: Works with any llama.cpp server or compatible endpoint
- **Dynamic Model Discovery**: Refresh button fetches available models from your server
- **GGUF Model Support**: Use quantized models (Q4, Q5, Q8) — far lower VRAM than FP16
- **Real-time Progress**: WebSocket-based live progress updates
- **GPU Resource Monitor**: Live CPU/RAM/GPU utilization via pynvml (no torch dependency)
- **Custom Prompts**: Save and reuse captioning prompts in a built-in library
- **Batch Processing**: Process entire folders of media files
- **Video Preview**: Hover to preview videos before processing
- **Thumbnail Caching**: Fast grid loading with cached thumbnails
- **Word Analytics**: Frequency analysis, n-grams, and word correlations across captions

### Supported Formats

| Type | Extensions |
|------|------------|
| Videos | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` |

## Project Structure

```
Video Caption Suite/
├── backend/
│   ├── api.py              # FastAPI server
│   ├── schemas.py          # Pydantic models
│   ├── processing.py       # Processing orchestration
│   ├── config.py           # Backend configuration
│   ├── model_loader.py     # OpenAI API client + caption generation
│   ├── video_processor.py  # Video/image frame extraction
│   └── resource_monitor.py # CPU/RAM/GPU metrics (pynvml)
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Root component
│   │   ├── components/     # Vue components
│   │   ├── stores/         # Pinia state management
│   │   ├── composables/    # Reusable logic
│   │   └── types/          # TypeScript definitions
│   └── package.json
├── requirements.txt        # Python dependencies
├── documentation/          # This documentation
└── CLAUDE.md              # AI assistant guidelines
```

## Hardware Requirements

The backend itself has no GPU requirement — all inference is handled by the llama.cpp server process.

### llama.cpp Server (Inference)
- NVIDIA GPU with enough VRAM for your chosen GGUF model:
  - Q4_K_M quantization: ~5–6 GB VRAM for a 7B model
  - Q8_0 quantization: ~8–9 GB VRAM for a 7B model
  - A 16 GB card handles most 7B–13B GGUF models comfortably

### Backend Host
- RAM: 4 GB minimum (no model weights stored in Python process)
- Storage: Space for media files and generated caption files

## Support

For issues, feature requests, or contributions, please refer to [DEVELOPMENT.md](./DEVELOPMENT.md).

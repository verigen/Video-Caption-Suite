# Architecture Overview

This document describes the system architecture, data flow, and component relationships of Video Caption Suite.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Vue 3)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  App.vue    │  │   Stores    │  │ Composables │  │     Components      │ │
│  │  (Root)     │  │  - video    │  │ - useApi    │  │  - Settings panels  │ │
│  │             │  │  - progress │  │ - useWS     │  │  - Video grid       │ │
│  │             │  │  - settings │  │ - useResize │  │  - Progress display │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                    HTTP REST   │   WebSocket
                    (port 5173) │   (ws://localhost:8000)
                                │
┌───────────────────────────────┴─────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         api.py (FastAPI Server)                         ││
│  │  - REST endpoints (settings, videos, captions, processing)              ││
│  │  - WebSocket endpoint (/ws/progress)                                    ││
│  │  - WebSocket endpoint (/ws/resources) — real-time resource monitoring   ││
│  │  - SSE streaming for video lists                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                         │
│  ┌──────────────────┐  ┌──────────┴───────────┐  ┌───────────────────────┐  │
│  │   schemas.py     │  │   processing.py      │  │  resource_monitor.py  │  │
│  │   (Pydantic)     │  │   (ProcessingMgr)    │  │  (CPU/RAM/GPU stats)  │  │
│  └──────────────────┘  └──────────┬───────────┘  └───────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────────────────┐
│                          CORE MODULES (backend/)                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │  backend/model_loader.py    │  │   backend/video_processor.py        │   │
│  │  - OpenAI API client        │  │  - Frame extraction (OpenCV)        │   │
│  │  - Base64 frame encoding    │  │  - Video metadata                   │   │
│  │  - Caption generation       │  │  - Resize/sampling                  │   │
│  │  - Server connectivity      │  │  - Directory scanning               │   │
│  └──────────────┬──────────────┘  └─────────────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────────────────┘
                │
                │  HTTP (OpenAI-compatible API)
                │
┌───────────────┴─────────────────────────────────────────────────────────────┐
│                         LLAMA.CPP SERVER                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  llama-server (or any OpenAI-compatible server)                         ││
│  │  - POST /v1/chat/completions  (image_url content blocks)                ││
│  │  - GET  /v1/models            (model discovery)                         ││
│  │                                                                         ││
│  │  Serves GGUF vision models (e.g. Qwen2.5-VL, LLaVA, etc.)             ││
│  │  Runs on GPU — stats visible in ResourceMonitor via pynvml              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Application Initialization

```
Browser loads App.vue
        │
        ├──► settingsStore.fetchSettings()
        │           │
        │           └──► GET /api/settings ──► Returns Settings JSON
        │
        ├──► videoStore.fetchVideos()
        │           │
        │           └──► GET /api/videos/stream (SSE)
        │                       │
        │                       └──► Streams video info progressively
        │                           (handles large libraries efficiently)
        │
        ├──► useWebSocket.connect()
        │           │
        │           └──► WS /ws/progress ──► Persistent connection
        │                                   for real-time updates
        │
        └──► useResourceWebSocket.connect()
                    │
                    └──► WS /ws/resources ──► Resource snapshots
                                             every 2 seconds
```

### 2. Video Processing Flow

```
User clicks "Process Selected Videos"
        │
        ▼
POST /api/process/start
  { video_names: [...] }
        │
        ▼
ProcessingManager.process_videos()
        │
        ├──► Check model loaded?
        │           │
        │    No ◄───┴───► Yes
        │    │              │
        │    ▼              │
        │  load_model()     │
        │    │              │
        │    └─► OpenAI(base_url=API_BASE_URL) client
        │    └─► client.models.list() — connectivity check
        │              │
        └──────────────┘
                │
                ▼
        For each video (sequential):
        ┌───────────────────────────────────────┐
        │  1. video_processor.process_video()   │
        │     └─► Extract frames (OpenCV)       │
        │     └─► Resize to frame_size          │
        │                                       │
        │  2. model_loader.generate_caption()   │
        │     └─► Encode frames as JPEG/base64  │
        │     └─► POST /v1/chat/completions     │
        │         (image_url blocks + text)     │
        │     └─► Return caption text           │
        │                                       │
        │  3. Save caption to .txt file         │
        │                                       │
        │  4. Emit progress via WebSocket       │
        │     └─► progressStore updates         │
        │     └─► UI re-renders                 │
        └───────────────────────────────────────┘
                │
                ▼
        Processing complete
        Stage = "complete"
```

### 3. Model Discovery Flow

```
User clicks "Refresh" in ModelSettings
        │
        ▼
GET /api/server/models
        │
        ▼
backend proxies GET /v1/models
to configured API_BASE_URL
        │
        ▼
Returns { models: ["model-name", ...], api_base_url: "..." }
        │
        ▼
Frontend shows dropdown of available models
User selects or types model name manually
```

## Component Relationships

### Backend Module Dependencies

```
api.py
  ├── schemas.py (Pydantic models)
  ├── processing.py (ProcessingManager)
  ├── resource_monitor.py (ResourceMonitor)
  └── config.py (settings)

resource_monitor.py
  ├── psutil (CPU and RAM metrics)
  └── pynvml / nvidia-ml-py3 (GPU metrics via NVML)

processing.py
  ├── model_loader.py (load_model, generate_caption, clear_cache)
  ├── video_processor.py (process_video)
  ├── schemas.py (Settings, ProgressUpdate)
  └── config.py

model_loader.py
  ├── config.py
  ├── openai (OpenAI SDK — HTTP client for llama.cpp server)
  ├── PIL (image encoding)
  ├── base64, io (frame serialization)
  └── time (latency measurement)

video_processor.py
  ├── config.py
  ├── os (scandir/walk for file discovery)
  └── cv2, PIL (external)

Note: All modules above are located in the `backend/` directory (e.g., `backend/config.py`, `backend/model_loader.py`, etc.).
```

### Frontend Component Hierarchy

```
App.vue
├── LayoutSidebar
│   └── SettingsPanel
│       ├── DirectorySettings
│       ├── ModelSettings
│       ├── InferenceSettings
│       ├── PromptSettings
│       └── PromptLibrary
│
├── VideoGrid (main content area)
│   ├── VideoGridToolbar
│   └── VideoTile (repeated)
│       ├── Thumbnail
│       ├── Selection checkbox
│       └── Caption preview
│
├── CaptionPanel (right sidebar)
│   └── CaptionViewer
│
├── ResourceMonitor (header)
│   └── Click-to-expand popover (per-GPU details)
│
└── StatusPanel / ProgressBar (header)
    ├── StageProgress
    ├── TokenCounter
    └── ProgressRing
```

### Store Dependencies

```
App.vue
  ├── useVideoStore()
  │     ├── videos, captions, selectedVideos
  │     └── fetchVideos(), toggleSelection()
  │
  ├── useProgressStore()
  │     ├── stage, progress
  │     └── updateFromWebSocket()
  │
  ├── useSettingsStore()
  │     ├── settings (api_base_url, api_model_name, ...)
  │     └── fetchSettings(), updateSettings()
  │
  └── useResourceStore()
        └── snapshot (CPU, RAM, GPU metrics via pynvml)

Composables:
  useWebSocket() ──► progressStore.updateFromWebSocket()
  useResourceWebSocket() ──► resourceStore.updateFromSnapshot()
  useApi() ──► HTTP requests to backend
```

## Key Design Decisions

### 1. WebSocket for Progress Updates
- Real-time updates without polling
- Automatic reconnection with exponential backoff
- Server broadcasts to all connected clients

### 2. SSE for Video Listing
- Handles large video libraries (1000+ files)
- Progressive loading improves perceived performance
- Reduces memory usage vs. single large response

### 3. OpenAI-Compatible API Client
- All inference is delegated to an external llama.cpp server (or any OpenAI-compatible endpoint)
- Frames are encoded as JPEG base64 and sent as `image_url` content blocks in the chat completions request
- No local model weights, no CUDA driver dependency in the Python process
- Server manages GPU memory; the backend is a thin HTTP client

### 4. No In-Process GPU Memory Management
- The backend never loads model weights, so there is no in-process VRAM to manage
- `clear_cache()` in `model_loader.py` is a no-op (kept for call-site compatibility)
- VRAM is managed entirely by the llama.cpp server process

### 5. Dedicated Resource Monitoring WebSocket
- Separate `/ws/resources` endpoint from `/ws/progress` to decouple resource metrics from processing state
- Uses `psutil` for CPU/RAM and `pynvml` (NVML) for per-GPU metrics (utilization, VRAM, temperature, power)
- Pushes snapshots every 2 seconds for near-real-time visibility while llama.cpp uses the GPU
- Dependencies: `psutil>=5.9.0`, `nvidia-ml-py3>=7.352.0`

### 6. Dynamic Model Discovery
- `GET /api/server/models` proxies `GET /v1/models` to the configured API server
- Users can refresh the model list at any time without restarting the backend
- Model name can also be typed manually (free-form) if the server doesn't expose `/v1/models`

## File Locations and Line References

| Component | File | Key Lines |
|-----------|------|-----------|
| FastAPI app creation | `backend/api.py` | 1-50 |
| WebSocket handler (progress) | `backend/api.py` | ~120-180 |
| WebSocket handler (resources) | `backend/api.py` | See `/ws/resources` |
| Server models endpoint | `backend/api.py` | See `/api/server/models` |
| Resource monitor | `backend/resource_monitor.py` | Full file |
| Video endpoints | `backend/api.py` | ~400-600 |
| Processing endpoints | `backend/api.py` | ~800-900 |
| ProcessingManager | `backend/processing.py` | Full file |
| API client (load_model) | `backend/model_loader.py` | `load_model()` |
| Caption generation | `backend/model_loader.py` | `generate_caption()` |
| Frame extraction | `backend/video_processor.py` | ~80-150 |
| Vue root component | `frontend/src/App.vue` | Full file |
| Video store | `frontend/src/stores/videoStore.ts` | Full file |
| Progress store | `frontend/src/stores/progressStore.ts` | Full file |
| Settings store | `frontend/src/stores/settingsStore.ts` | Full file |
| WebSocket composable | `frontend/src/composables/useWebSocket.ts` | Full file |

## Security Considerations

1. **Path Traversal Prevention**: All file paths validated against `..` sequences
2. **Input Validation**: Pydantic models enforce type constraints
3. **CORS**: Configured for development; tighten for production
4. **No Authentication**: Currently designed for local use only

## Performance Optimizations

### Model Inference
1. **GGUF Quantization**: llama.cpp serves quantized models (Q4, Q5, Q8 etc.) — far smaller VRAM footprint than FP16
2. **Frame Count Control**: `max_frames` setting limits how many base64 image blocks are sent per request
3. **JPEG Quality**: Frames are compressed to JPEG quality 85 before base64 encoding to reduce token count

### Media Loading
4. **Single-Pass File Discovery**: `find_all_media()` in `backend/video_processor.py` uses `os.scandir()` (flat) or `os.walk()` (recursive) with pre-computed extension sets, replacing 16-28 per-extension `glob()` calls with a single directory traversal
5. **PIL Image Thumbnails**: Image files use `Pillow` for thumbnail generation (fast), while video files use `ffmpeg`. Routed automatically by file extension via `_generate_any_thumbnail()`
6. **Background Thumbnail Pre-generation**: After SSE streaming completes, `asyncio.create_task()` kicks off a `ThreadPoolExecutor(max_workers=4)` to pre-generate all uncached thumbnails in batches of 50
7. **Non-blocking Thumbnail Endpoint**: On-demand thumbnail requests use `asyncio.to_thread()` so generation doesn't block the FastAPI event loop
8. **Caption Preview Optimization**: Only reads first 200 bytes of caption files for preview text, instead of loading entire files

### Frontend
9. **Virtual Scrolling**: Efficient rendering of large video grids (only visible + buffer rows)
10. **SSE Batch Throttling**: Incoming video batches accumulate in a plain (non-reactive) array and flush to Vue reactive state at most every 150ms, reducing reactivity cascades from ~50 to ~10 for large libraries
11. **Video Preview `preload="none"`**: Hover preview video elements use `preload="none"` to prevent browsers from downloading video data until playback starts
12. **Thumbnail Caching**: MD5-based cache avoids regeneration on subsequent loads

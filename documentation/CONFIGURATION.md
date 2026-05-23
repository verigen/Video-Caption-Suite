# Configuration Reference

Complete reference for all configuration options in Video Caption Suite.

## Configuration Files

| File | Purpose |
|------|---------|
| `backend/config.py` | Backend Python settings |
| `user_config.json` | User working directory and preferences (auto-generated, persisted) |
| `settings.json` | Persisted user settings (auto-generated) |
| `prompts.json` | Saved prompt library (auto-generated) |
| `frontend/vite.config.ts` | Frontend build configuration |
| `frontend/tailwind.config.js` | CSS framework configuration |

---

## Backend Configuration (backend/config.py)

**File:** `backend/config.py`

### API Server Settings

```python
# Base URL of the OpenAI-compatible server (llama.cpp or any compatible server)
API_BASE_URL = "http://localhost:8080"

# API key — leave empty for local servers that don't require authentication
API_KEY = ""

# Default model name as reported by GET /v1/models on the server
API_MODEL_NAME = ""
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `API_BASE_URL` | str | `"http://localhost:8080"` | Base URL of your llama.cpp (or compatible) server |
| `API_KEY` | str | `""` | Optional API key (most local servers don't need one) |
| `API_MODEL_NAME` | str | `""` | Default model name; discovered dynamically if empty |

These defaults are overridden by `settings.json` at runtime when the user saves settings in the UI.

### Inference Settings

```python
# Maximum frames to extract per video
MAX_FRAMES_PER_VIDEO = 128

# Frame resize target (pixels, preserves aspect ratio)
FRAME_SIZE = 336

# Maximum tokens to generate
MAX_TOKENS = 512

# Sampling temperature (0 = greedy, higher = more creative)
TEMPERATURE = 0.3
```

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `MAX_FRAMES_PER_VIDEO` | int | `128` | 1-128 | More frames = better temporal understanding |
| `FRAME_SIZE` | int | `336` | 224-672 | Larger = more detail sent to server |
| `MAX_TOKENS` | int | `512` | 64-2048 | Maximum caption length |
| `TEMPERATURE` | float | `0.3` | 0.0-2.0 | 0 = deterministic, >1 = very creative |

### Directory Settings

```python
# Default working directory (persisted to user_config.json)
WORKING_DIRECTORY = None  # Set via API

# Search subfolders for videos (persisted to user_config.json)
TRAVERSE_SUBFOLDERS = False

# Output file extension
OUTPUT_EXTENSION = ".txt"
```

| Setting | Type | Default | Persisted | Description |
|---------|------|---------|-----------|-------------|
| `WORKING_DIRECTORY` | str/None | `None` | Yes | Video source folder |
| `TRAVERSE_SUBFOLDERS` | bool | `False` | Yes | Recursively search subfolders |
| `OUTPUT_EXTENSION` | str | `.txt` | No | Caption file extension |

---

## User Config (user_config.json)

**Location:** Project root (auto-generated)

Stores the user's working directory, folder preferences, and media type filters. Automatically loaded on server startup and saved when settings change.

```json
{
  "working_directory": "/home/user/Videos/MyProject",
  "traverse_subfolders": false,
  "include_videos": true,
  "include_images": false
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `working_directory` | string/null | `null` | Path to media source folder |
| `traverse_subfolders` | bool | `false` | Whether to search subfolders |
| `include_videos` | bool | `true` | Include video files in media list |
| `include_images` | bool | `false` | Include image files in media list |

---

## User Settings (settings.json)

**Location:** Project root (auto-generated)

Settings are persisted when changed via the API. All fields from `backend/schemas.py:Settings`.

```json
{
  "api_base_url": "http://localhost:8080",
  "api_key": "",
  "api_model_name": "qwen2.5-vl-7b",
  "max_frames": 16,
  "frame_size": 336,
  "max_tokens": 512,
  "temperature": 0.3,
  "prompt": "Describe this video in detail...",
  "include_metadata": false
}
```

### Settings Schema

| Field | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `api_base_url` | string | `"http://localhost:8080"` | - | OpenAI-compatible server URL |
| `api_key` | string | `""` | - | API key (empty = local server) |
| `api_model_name` | string | `""` | - | Model name as reported by server |
| `max_frames` | int | `16` | 1-128 | Frames per video |
| `frame_size` | int | `336` | 224-672 | Frame dimensions (pixels) |
| `max_tokens` | int | `512` | 64-2048 | Output length |
| `temperature` | float | `0.3` | 0.0-2.0 | Creativity |
| `prompt` | string | See default | - | Captioning prompt |
| `include_metadata` | bool | `false` | - | Add metadata to output files |

---

## Prompt Library (prompts.json)

**Location:** Project root (auto-generated)

```json
{
  "prompts": [
    {
      "id": "abc123-def456",
      "name": "Detailed Description",
      "prompt": "Describe this video...",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## Frontend Configuration

### Vite Configuration

**File:** `frontend/vite.config.ts`

```typescript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

---

## Performance Tuning

### For Speed

```json
{
  "max_frames": 8,
  "frame_size": 224,
  "max_tokens": 256,
  "temperature": 0.0
}
```

### For Quality

```json
{
  "max_frames": 32,
  "frame_size": 512,
  "max_tokens": 1024,
  "temperature": 0.3
}
```

### Frame Count Guidelines

- **Images**: Always 1 frame
- **Short clips (< 10s)**: 8-16 frames
- **Medium videos (10-60s)**: 16-32 frames
- **Long videos (> 60s)**: 32-64 frames

The optimal frame count is ultimately a function of your server's context window and the model's vision token budget.

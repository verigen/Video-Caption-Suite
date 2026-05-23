# API Reference

Complete reference for the Video Caption Suite REST and WebSocket APIs.

**Base URL:** `http://localhost:8000`
**WebSocket:** `ws://localhost:8000/ws/progress` | `ws://localhost:8000/ws/resources`

## Table of Contents

- [Settings Endpoints](#settings-endpoints)
- [System Endpoints](#system-endpoints)
- [Directory Endpoints](#directory-endpoints)
- [Prompt Library Endpoints](#prompt-library-endpoints)
- [Video Endpoints](#video-endpoints)
- [Caption Endpoints](#caption-endpoints)
- [Model Endpoints](#model-endpoints)
- [Processing Endpoints](#processing-endpoints)
- [Analytics Endpoints](#analytics-endpoints)
- [WebSocket API](#websocket-api)

---

## Settings Endpoints

### GET /api/settings

Retrieve current application settings.

**Response:**
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

**File Reference:** `backend/api.py`

---

### POST /api/settings

Update settings (partial update supported).

**Request Body:** (all fields optional)
```json
{
  "api_model_name": "qwen2.5-vl-7b",
  "max_frames": 32,
  "temperature": 0.5
}
```

**Response:** Updated `Settings` object (same shape as GET).

**File Reference:** `backend/api.py`

---

### POST /api/settings/reset

Reset all settings to defaults.

**Response:** Default `Settings` object.

---

### GET /api/server/models

List models available on the currently configured API server. The backend proxies `GET /v1/models` from the server specified in `api_base_url`.

**Response:**
```json
{
  "models": ["qwen2.5-vl-7b", "llava-1.6-mistral-7b"],
  "api_base_url": "http://localhost:8080"
}
```

**Error (502):** Server unreachable — check `api_base_url` setting.

**File Reference:** `backend/api.py`

---

## Directory Endpoints

### GET /api/directory

Get current working directory, subfolder setting, and media type filters.

**Response:**
```json
{
  "directory": "C:/Videos/MyProject",
  "video_count": 42,
  "image_count": 15,
  "traverse_subfolders": true,
  "include_videos": true,
  "include_images": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `directory` | string | Current working directory path |
| `video_count` | number | Number of video files found |
| `image_count` | number | Number of image files found |
| `traverse_subfolders` | boolean | Whether to search subdirectories |
| `include_videos` | boolean | Whether to include video files |
| `include_images` | boolean | Whether to include image files |

**File Reference:** `backend/api.py:280-295`

---

### POST /api/directory

Set working directory and media type filters.

**Request Body:**
```json
{
  "directory": "C:/Videos/NewProject",
  "traverse_subfolders": false,
  "include_videos": true,
  "include_images": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `directory` | string | Yes | - | Directory path to set |
| `traverse_subfolders` | boolean | No | `false` | Search subdirectories |
| `include_videos` | boolean | No | `true` | Include video files |
| `include_images` | boolean | No | `false` | Include image files |

**Response:**
```json
{
  "directory": "C:/Videos/NewProject",
  "video_count": 30,
  "image_count": 25,
  "traverse_subfolders": false,
  "include_videos": true,
  "include_images": true
}
```

**Errors:**
- `400 Bad Request`: Directory does not exist
- `400 Bad Request`: Path contains invalid characters (`..`)

**File Reference:** `backend/api.py:298-330`

---

### GET /api/directory/browse

Browse directories for the folder picker UI.

**Query Parameters:**
- `path` (optional): Directory path to browse. If omitted, returns root drives (Windows) or `/` (Unix).

**Response:**
```json
{
  "current_path": "C:/Videos",
  "parent_path": "C:/",
  "directories": [
    {"name": "Project1", "path": "C:/Videos/Project1"},
    {"name": "Project2", "path": "C:/Videos/Project2"}
  ]
}
```

**File Reference:** `backend/api.py:333-390`

---

## Prompt Library Endpoints

### GET /api/prompts

List all saved prompts.

**Response:**
```json
{
  "prompts": [
    {
      "id": "abc123",
      "name": "Detailed Description",
      "prompt": "Describe this video in detail including...",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**File Reference:** `backend/api.py:200-220`

---

### POST /api/prompts

Create a new prompt.

**Request Body:**
```json
{
  "name": "Action Scene",
  "prompt": "Describe the action and movement in this video..."
}
```

**Response:**
```json
{
  "id": "xyz789",
  "name": "Action Scene",
  "prompt": "Describe the action and movement...",
  "created_at": "2025-01-20T15:00:00Z",
  "updated_at": "2025-01-20T15:00:00Z"
}
```

**File Reference:** `backend/api.py:223-245`

---

### GET /api/prompts/{prompt_id}

Get a specific prompt by ID.

**Response:**
```json
{
  "id": "abc123",
  "name": "Detailed Description",
  "prompt": "Describe this video...",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errors:**
- `404 Not Found`: Prompt not found

**File Reference:** `backend/api.py:248-260`

---

### PUT /api/prompts/{prompt_id}

Update an existing prompt.

**Request Body:**
```json
{
  "name": "Updated Name",
  "prompt": "Updated prompt text..."
}
```

**Response:** Updated prompt object

**File Reference:** `backend/api.py:263-280`

---

### DELETE /api/prompts/{prompt_id}

Delete a prompt.

**Response:**
```json
{
  "success": true
}
```

**File Reference:** `backend/api.py:283-295`

---

## Media Endpoints

### GET /api/videos

List all media files (videos and images) in the working directory.

**Response:**
```json
{
  "videos": [
    {
      "name": "video1.mp4",
      "path": "C:/Videos/video1.mp4",
      "size_mb": 100.0,
      "media_type": "video",
      "duration_sec": 120.5,
      "width": 1920,
      "height": 1080,
      "frame_count": 3615,
      "fps": 30.0,
      "has_caption": true,
      "caption_preview": "A person walking..."
    },
    {
      "name": "image1.jpg",
      "path": "C:/Videos/image1.jpg",
      "size_mb": 2.5,
      "media_type": "image",
      "duration_sec": null,
      "width": 1920,
      "height": 1080,
      "frame_count": 1,
      "fps": null,
      "has_caption": false,
      "caption_preview": null
    }
  ],
  "total": 150,
  "directory": "C:/Videos"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `media_type` | string | Either `"video"` or `"image"` |
| `duration_sec` | number/null | Duration in seconds (videos only) |
| `frame_count` | number/null | Frame count (1 for images) |
| `fps` | number/null | Frames per second (videos only) |

**Note:** Which media types are returned depends on the `include_videos` and `include_images` settings (see Directory endpoints).

**File Reference:** `backend/api.py:400-450`

---

### GET /api/videos/stream

Stream media list via Server-Sent Events (SSE). Preferred for large libraries.

**Response:** SSE stream with events:
```
event: video
data: {"name": "video1.mp4", "media_type": "video", "size_mb": 100.0, ...}

event: video
data: {"name": "image1.jpg", "media_type": "image", "size_mb": 2.5, ...}

event: complete
data: {"total": 150}
```

**File Reference:** `backend/api.py:453-510`

---

### POST /api/videos/upload

Upload a video file.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "success": true,
  "video": {
    "name": "uploaded_video.mp4",
    "path": "C:/Videos/uploaded_video.mp4",
    "size_bytes": 52428800
  }
}
```

**File Reference:** `backend/api.py:513-545`

---

### DELETE /api/videos/{video_name}

Delete a video file.

**Response:**
```json
{
  "success": true
}
```

**Errors:**
- `404 Not Found`: Video not found
- `400 Bad Request`: Invalid filename

**File Reference:** `backend/api.py:548-570`

---

### GET /api/videos/{video_name}/thumbnail

Get media thumbnail (generated and cached).

**Response:** JPEG image (`image/jpeg`)

**Query Parameters:**
- `size` (optional, default: 160): Thumbnail size in pixels (clamped 64-320)

**Caching:** Thumbnails are cached in `.thumbnail_cache/` with MD5-based filenames keyed on file name, mtime, size, and requested dimensions.

**Generation:**
- **Videos:** Uses ffmpeg to extract a frame at 1 second
- **Images:** Uses PIL for fast resize and center-crop
- **Background pre-generation:** After the SSE media stream completes, uncached thumbnails are generated in background using a 4-thread pool
- On-demand generation runs in a separate thread to avoid blocking the API

**File Reference:** `backend/api.py:596-720`

---

### GET /api/videos/{video_name}/stream

Stream video for preview playback.

**Response:** Video stream with range request support (`video/mp4`)

**File Reference:** `backend/api.py:613-645`

---

## Caption Endpoints

### GET /api/captions

List all generated captions.

**Response:**
```json
{
  "captions": [
    {
      "video_name": "video1.mp4",
      "caption_path": "C:/Videos/video1.txt",
      "caption_text": "This video shows...",
      "created_at": "2025-01-20T14:30:00Z"
    }
  ]
}
```

**File Reference:** `backend/api.py:733-760`

---

### GET /api/captions/{video_name}

Get caption for a specific video.

**Response:**
```json
{
  "video_name": "video1.mp4",
  "caption_path": "C:/Videos/video1.txt",
  "caption_text": "This video shows a person walking...",
  "created_at": "2025-01-20T14:30:00Z"
}
```

**Errors:**
- `404 Not Found`: Caption not found

**File Reference:** `backend/api.py:763-785`

---

### DELETE /api/captions/{video_name}

Delete a caption file.

**Response:**
```json
{
  "success": true
}
```

**File Reference:** `backend/api.py:788-805`

---

## Model Endpoints

### GET /api/model/status

Get current API server connection status.

**Response:**
```json
{
  "loaded": true,
  "model_id": "qwen2.5-vl-7b",
  "api_base_url": "http://localhost:8080",
  "available_models": ["qwen2.5-vl-7b"]
}
```

**File Reference:** `backend/api.py`

---

### POST /api/model/load

Connect to the API server (optional — happens automatically on first process).

**Response:**
```json
{
  "success": true,
  "message": "Connected to API server"
}
```

**File Reference:** `backend/api.py`

---

### POST /api/model/unload

Disconnect from the API server.

**Response:**
```json
{
  "success": true,
  "message": "Model unloaded"
}
```

**Errors:**
- `409 Conflict`: Processing in progress

**File Reference:** `backend/api.py`

---

## Processing Endpoints

### POST /api/process/start

Start video processing.

**Request Body:** (all fields optional)
```json
{
  "video_names": ["video1.mp4", "video2.mp4"],
  "settings": {
    "max_frames": 64,
    "temperature": 0.5
  }
}
```

If `video_names` is omitted, processes all uncaptioned videos.

**Response:**
```json
{
  "success": true,
  "message": "Processing started",
  "total_videos": 5
}
```

**Errors:**
- `409 Conflict`: Processing already in progress

**File Reference:** `backend/api.py:800-870`

---

### POST /api/process/stop

Stop current processing.

**Response:**
```json
{
  "success": true,
  "message": "Processing stopped"
}
```

**File Reference:** `backend/api.py:873-890`

---

### GET /api/process/status

Get current processing status.

**Response:**
```json
{
  "stage": "processing",
  "current_video": "video3.mp4",
  "video_index": 2,
  "total_videos": 10,
  "completed_videos": 2,
  "tokens_generated": 1547,
  "tokens_per_sec": 45.2,
  "model_loaded": true,
  "substage": "generating",
  "substage_progress": 0.65,
  "elapsed_time": 125.4
}
```

**File Reference:** `backend/api.py`

---

## Analytics Endpoints

Analyze word patterns across generated captions.

### GET /api/analytics/summary

Get quick statistics about the caption dataset.

**Response:**
```json
{
  "total_captions": 150,
  "total_words": 45230,
  "unique_words": 3421,
  "avg_words_per_caption": 301.5,
  "top_words": [
    {"word": "video", "count": 892, "frequency": 0.0197},
    {"word": "shows", "count": 654, "frequency": 0.0145}
  ]
}
```

**File Reference:** `backend/api.py`

---

### POST /api/analytics/wordfreq

Analyze word frequency across captions.

**Request Body:**
```json
{
  "video_names": ["video1.mp4", "video2.mp4"],
  "stopword_preset": "english",
  "custom_stopwords": ["specific", "words"],
  "min_word_length": 2,
  "top_n": 50
}
```

All fields optional. `video_names` = null analyzes all captions.

**Stopword Presets:**
- `none`: No stopwords filtered
- `minimal`: Basic function words (the, a, an, is, are)
- `english`: Comprehensive English stopwords (200+ words)

**Response:**
```json
{
  "words": [
    {"word": "person", "count": 234, "frequency": 0.0051},
    {"word": "walking", "count": 189, "frequency": 0.0042}
  ],
  "total_words": 45230,
  "total_unique_words": 3421,
  "captions_analyzed": 150,
  "analysis_time_ms": 45.2
}
```

**File Reference:** `backend/api.py`, `backend/analytics.py`

---

### POST /api/analytics/ngrams

Analyze n-gram (word sequences) frequency.

**Request Body:**
```json
{
  "video_names": null,
  "n": 2,
  "stopword_preset": "english",
  "top_n": 30,
  "min_count": 2
}
```

**Parameters:**
- `n`: 2 = bigrams, 3 = trigrams, 4 = 4-grams (default: 2)
- `min_count`: Minimum occurrence count to include (default: 2)

**Response:**
```json
{
  "ngrams": [
    {"ngram": ["person", "walking"], "display": "person walking", "count": 45, "frequency": 0.0023},
    {"ngram": ["camera", "pans"], "display": "camera pans", "count": 38, "frequency": 0.0019}
  ],
  "n": 2,
  "total_ngrams": 12450,
  "captions_analyzed": 150
}
```

**File Reference:** `backend/api.py`, `backend/analytics.py`

---

### POST /api/analytics/correlations

Analyze word co-occurrence and correlations using PMI (Pointwise Mutual Information).

**Request Body:**
```json
{
  "video_names": null,
  "target_words": ["person", "camera"],
  "window_size": 5,
  "min_co_occurrence": 3,
  "top_n": 50
}
```

**Parameters:**
- `target_words`: Optional list of words to focus on (null = all words)
- `window_size`: Word context window for co-occurrence (default: 5)
- `min_co_occurrence`: Minimum times words appear together (default: 3)

**Response:**
```json
{
  "correlations": [
    {"word1": "person", "word2": "walking", "co_occurrence": 89, "pmi_score": 3.45},
    {"word1": "camera", "word2": "pans", "co_occurrence": 67, "pmi_score": 4.12}
  ],
  "nodes": ["person", "walking", "camera", "pans", "scene"],
  "captions_analyzed": 150
}
```

**PMI Score:**
- Positive: Words appear together more than expected by chance
- Negative: Words appear together less than expected
- Higher absolute value = stronger association

**File Reference:** `backend/api.py`, `backend/analytics.py`

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress');
```

### Messages Received

**Progress Update:**
```json
{
  "type": "progress",
  "data": {
    "stage": "processing",
    "current_video": "video2.mp4",
    "video_index": 1,
    "total_videos": 5,
    "completed_videos": 1,
    "tokens_generated": 256,
    "tokens_per_sec": 42.5,
    "model_loaded": true,
    "substage": "generating",
    "substage_progress": 0.45,
    "elapsed_time": 30.2,
    "just_completed_video": "video1.mp4",
    "just_completed_caption_preview": "A person walks through a sunlit park..."
  }
}
```

**Completion Event Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `just_completed_video` | `string \| null` | Relative path of the video that just finished processing. Only set on the message immediately after a video completes; `null` on all other messages. |
| `just_completed_caption_preview` | `string \| null` | First 150 characters of the generated caption. Only set when `just_completed_video` is set and processing succeeded. |

The frontend uses these transient fields to immediately mark tiles as captioned and update caption previews in real-time without requiring a page refresh.

**File Reference:** `backend/api.py:120-180`

### Ping/Pong

The frontend sends periodic pings to keep the connection alive:

```javascript
// Client sends
ws.send(JSON.stringify({ type: 'ping' }));

// Server responds
{ "type": "pong" }
```

### Reconnection

The frontend automatically reconnects with exponential backoff:
- Initial delay: 1 second
- Max delay: 30 seconds
- Max attempts: 5

**File Reference:** `frontend/src/composables/useWebSocket.ts`

---

### Resource Monitoring WebSocket

#### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/resources');
```

A dedicated WebSocket endpoint for real-time system resource monitoring. Operates independently from the progress WebSocket, so resource metrics are available regardless of whether processing is active.

#### Messages Received

The server sends a `ResourceUpdate` snapshot every **2 seconds**:

```json
{
  "cpu_percent": 45.2,
  "ram_used_gb": 12.4,
  "ram_total_gb": 32.0,
  "gpus": [
    {
      "index": 0,
      "name": "NVIDIA GeForce RTX 4090",
      "utilization_percent": 78.0,
      "vram_used_gb": 16.2,
      "vram_total_gb": 24.0,
      "temperature_c": 72,
      "power_draw_w": 320.5,
      "power_limit_w": 450.0
    },
    {
      "index": 1,
      "name": "NVIDIA GeForce RTX 4090",
      "utilization_percent": 65.0,
      "vram_used_gb": 15.8,
      "vram_total_gb": 24.0,
      "temperature_c": 68,
      "power_draw_w": 290.0,
      "power_limit_w": 450.0
    }
  ],
  "timestamp": "2025-01-20T14:30:00.123Z"
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `cpu_percent` | number | System-wide CPU utilization (0-100) |
| `ram_used_gb` | number | RAM currently in use (GB) |
| `ram_total_gb` | number | Total system RAM (GB) |
| `gpus` | array | Per-GPU metrics (see below) |
| `timestamp` | string | ISO 8601 timestamp of the snapshot |

**Per-GPU Fields (`GPUResourceMetrics`):**

| Field | Type | Description |
|-------|------|-------------|
| `index` | number | GPU device index |
| `name` | string | GPU model name |
| `utilization_percent` | number | GPU core utilization (0-100) |
| `vram_used_gb` | number | VRAM currently in use (GB) |
| `vram_total_gb` | number | Total VRAM (GB) |
| `temperature_c` | number | GPU temperature in Celsius |
| `power_draw_w` | number | Current power draw (Watts) |
| `power_limit_w` | number | Power limit (Watts) |

**Backend Implementation:** Uses `psutil` for CPU/RAM metrics and `pynvml` (NVML) for GPU metrics. The `ResourceMonitor` class in `backend/resource_monitor.py` collects all metrics per snapshot.

**File Reference:** `backend/api.py`, `backend/resource_monitor.py`, `backend/schemas.py`

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing the problem"
}
```

**Common HTTP Status Codes:**
- `400 Bad Request`: Invalid input or parameters
- `404 Not Found`: Resource not found
- `409 Conflict`: Operation conflicts with current state
- `500 Internal Server Error`: Server-side error

---

## Rate Limiting

Currently no rate limiting is implemented. The API is designed for local use.

---

## CORS Configuration

CORS is configured to allow all origins in development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production deployment, restrict `allow_origins` to specific domains.

**File Reference:** `backend/api.py:50-60`

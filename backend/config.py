"""
Configuration for Video Caption Suite
All settings in one place for easy tuning
"""

import json
import os
from pathlib import Path
from typing import Optional

# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
USER_CONFIG_FILE = PROJECT_ROOT / "user_config.json"

# =============================================================================
# WORKING DIRECTORY (User-configurable)
# =============================================================================

_current_working_dir: Optional[Path] = None
_traverse_subfolders: bool = False
_include_videos: bool = True
_include_images: bool = False

# Default to user's home directory
_default_working_dir = Path.home()


def _load_user_config() -> None:
    """Load user config from JSON file on startup"""
    global _current_working_dir, _traverse_subfolders, _include_videos, _include_images

    if USER_CONFIG_FILE.exists():
        try:
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Restore working directory if it exists and is valid
            if 'working_directory' in config and config['working_directory']:
                path = Path(config['working_directory'])
                if path.exists() and path.is_dir():
                    _current_working_dir = path

            # Restore traverse subfolders setting
            if 'traverse_subfolders' in config:
                _traverse_subfolders = bool(config['traverse_subfolders'])

            # Restore media type filters
            if 'include_videos' in config:
                _include_videos = bool(config['include_videos'])
            if 'include_images' in config:
                _include_images = bool(config['include_images'])

        except (json.JSONDecodeError, IOError):
            # If config is corrupted, start fresh
            pass


def _save_user_config() -> None:
    """Save user config to JSON file"""
    config = {
        'working_directory': str(_current_working_dir) if _current_working_dir else None,
        'traverse_subfolders': _traverse_subfolders,
        'include_videos': _include_videos,
        'include_images': _include_images
    }

    try:
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except IOError:
        # Silently fail if we can't write config
        pass


def get_working_directory() -> Path:
    """Returns current working directory or default (user's home)"""
    return _current_working_dir or _default_working_dir


def set_working_directory(path: Path) -> None:
    """Set the working directory for videos and captions"""
    global _current_working_dir
    _current_working_dir = path
    _save_user_config()


def get_working_directory_str() -> str:
    """Returns current working directory as string"""
    return str(get_working_directory())


def get_traverse_subfolders() -> bool:
    """Returns whether to traverse subfolders when finding videos"""
    return _traverse_subfolders


def set_traverse_subfolders(traverse: bool) -> None:
    """Set whether to traverse subfolders when finding videos"""
    global _traverse_subfolders
    _traverse_subfolders = traverse
    _save_user_config()


def get_include_videos() -> bool:
    """Returns whether to include videos in media search"""
    return _include_videos


def set_include_videos(include: bool) -> None:
    """Set whether to include videos in media search"""
    global _include_videos
    _include_videos = include
    _save_user_config()


def get_include_images() -> bool:
    """Returns whether to include images in media search"""
    return _include_images


def set_include_images(include: bool) -> None:
    """Set whether to include images in media search"""
    global _include_images
    _include_images = include
    _save_user_config()


# Load user config on module import
_load_user_config()

# =============================================================================
# API SERVER SETTINGS
# =============================================================================

# Base URL of the OpenAI-compatible API server (e.g. llama.cpp server)
API_BASE_URL = "http://localhost:8080"

# API key — leave empty for local servers that don't require authentication
API_KEY = ""

# Default model name as reported by the server's /v1/models endpoint
API_MODEL_NAME = ""

# Log every API request/response to a file.
# Enable by setting the env var:  LOG_API_CALLS=1  (or "true" / "yes")
LOG_API_CALLS: bool = os.getenv("LOG_API_CALLS", "").lower() in ("1", "true", "yes")
API_LOG_FILE: Path = PROJECT_ROOT / "api_calls.log"

# =============================================================================
# INFERENCE SETTINGS
# =============================================================================

# Maximum frames to extract from each video
# More frames = better understanding but slower inference
MAX_FRAMES_PER_VIDEO = 128

# Frame size in pixels (max dimension)
# Smaller = faster but less detail
# Range: 224 - 672 (multiples of 56 work best)
FRAME_SIZE = 336

# Maximum tokens to generate per caption
MAX_TOKENS = 512

# Temperature for generation (0.0 = deterministic, higher = more creative)
# Lower values are more stable and factual
TEMPERATURE = 0.3

# Default prompt for captioning
DEFAULT_PROMPT = """Describe this video in detail. Include:
- The main subject and their actions
- The setting and environment
- Any notable objects or elements
- The overall mood or atmosphere
- Any text visible in the video"""

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# File extension for output captions
OUTPUT_EXTENSION = ".txt"

# Include metadata in output (timing, token counts, etc.)
INCLUDE_METADATA = False

# =============================================================================
# MEDIA FILE EXTENSIONS
# =============================================================================

VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".webm",
    ".flv", ".wmv", ".m4v", ".mpeg", ".mpg"
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"
}

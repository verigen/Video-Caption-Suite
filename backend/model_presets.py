"""
Model presets — removed in favour of dynamic API model discovery.

The preset registry (HuggingFace model IDs, VRAM estimates, torch flags) is
no longer needed because inference runs on an external OpenAI-compatible
server (llama.cpp). Models are discovered at runtime via GET /v1/models.

This module is kept as a minimal stub so that any lingering import in other
files doesn't break. It exports no meaningful presets.
"""

from typing import Dict, Any, Optional

MODEL_PRESETS: Dict[str, Dict[str, Any]] = {}

DEFAULT_PRESET = ""


def get_preset(preset_id: str) -> Optional[Dict[str, Any]]:
    return MODEL_PRESETS.get(preset_id)


def resolve_preset(preset_id: Optional[str], model_id: Optional[str]) -> Dict[str, Any]:
    return {"loader": "openai_api"}


def list_presets_public() -> list:
    return []


def frame_size_for_preset(preset: Dict[str, Any], requested: int) -> int:
    return requested

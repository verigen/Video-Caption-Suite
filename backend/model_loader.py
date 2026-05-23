"""
Model loader — OpenAI-compatible API client.

Replaces local torch inference with HTTP calls to an OpenAI-compatible
server (e.g. llama.cpp). The public interface (load_model, generate_caption,
clear_cache) stays identical so processing.py needs no changes.
"""

import base64
import io
import time
from typing import Dict, Any, Tuple, List, Optional

from openai import OpenAI

from backend import config


def load_model(
    model_id: str = None,
    device: str = None,
    dtype: str = None,
    use_sage_attention: bool = None,
    use_torch_compile: bool = None,
    force_reload: bool = False,
    preset_id: str = None,
) -> Dict[str, Any]:
    """
    Connect to the configured API server and return a model_info dict.

    All torch-specific parameters (device, dtype, use_sage_attention,
    use_torch_compile) are accepted but ignored — they exist only to keep
    call-sites in processing.py unchanged.
    """
    api_base_url = config.API_BASE_URL
    api_key = config.API_KEY or "none"
    api_model_name = model_id or config.API_MODEL_NAME

    print("\n" + "=" * 60)
    print("[Model Loader] CONNECTING TO API SERVER")
    print("=" * 60)
    print(f"[Model Loader] Server: {api_base_url}")
    print(f"[Model Loader] Model: {api_model_name or '(will discover from server)'}")
    print("=" * 60 + "\n")

    client = OpenAI(base_url=api_base_url, api_key=api_key)

    # Connectivity check — raises if the server is unreachable
    available_models = [m.id for m in client.models.list().data]

    if api_model_name and api_model_name not in available_models:
        print(f"[Model Loader] Warning: '{api_model_name}' not in server model list: {available_models}")

    if not api_model_name and available_models:
        api_model_name = available_models[0]
        print(f"[Model Loader] No model specified, defaulting to first available: {api_model_name}")

    print(f"[Model Loader] Connected. Available models: {available_models}")

    return {
        "client": client,
        "api_model_name": api_model_name,
        "api_base_url": api_base_url,
        "available_models": available_models,
        # Kept for compatibility with code that reads these fields
        "model_id": api_model_name,
        "preset_id": None,
        "preset": {"loader": "openai_api"},
        "device": None,
        "dtype": None,
        "sage_attention": False,
        "torch_compiled": False,
        "device_map": None,
    }


def generate_caption(
    model_info: Dict[str, Any],
    images: list,
    prompt: str,
    max_tokens: int = None,
    temperature: float = None,
    video_fps: float = None,
) -> Tuple[str, Dict[str, Any]]:
    """Generate a caption by sending frames to the API server."""
    max_tokens = max_tokens or config.MAX_TOKENS
    temperature = temperature if temperature is not None else config.TEMPERATURE

    client: OpenAI = model_info["client"]
    api_model_name: str = model_info["api_model_name"]

    # Encode each frame as a base64 JPEG image_url content block
    content: List[Dict[str, Any]] = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })
    content.append({"type": "text", "text": prompt})

    t0 = time.time()
    response = client.chat.completions.create(
        model=api_model_name,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    elapsed = time.time() - t0

    output_text = response.choices[0].message.content or ""
    in_tokens = response.usage.prompt_tokens if response.usage else 0
    out_tokens = response.usage.completion_tokens if response.usage else 0

    return output_text.strip(), {
        "input_tokens": in_tokens,
        "output_tokens": out_tokens,
        "total_time": elapsed,
        "tokens_per_sec": out_tokens / elapsed if elapsed > 0 else 0,
        "num_frames": len(images),
    }


def clear_cache() -> None:
    """No-op — the API server manages its own model state."""
    pass

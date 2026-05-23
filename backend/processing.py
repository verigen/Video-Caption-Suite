"""
Processing manager for video captioning via OpenAI-compatible API.
"""

import asyncio
import time
from pathlib import Path
from typing import Callable, Optional, List, Any, Dict
from dataclasses import dataclass

from backend.schemas import (
    Settings, ProgressUpdate, ProcessingStage, ProcessingSubstage, MediaType
)


@dataclass
class ProcessingState:
    """Mutable state for tracking processing progress"""
    stage: ProcessingStage = ProcessingStage.IDLE
    current_video: Optional[str] = None
    video_index: int = 0
    total_videos: int = 0
    completed_videos: int = 0
    tokens_generated: int = 0
    tokens_per_sec: float = 0.0
    model_loaded: bool = False
    substage: ProcessingSubstage = ProcessingSubstage.IDLE
    substage_progress: float = 0.0
    error_message: Optional[str] = None
    start_time: float = 0.0
    # Transient completion event (cleared after each emit)
    _just_completed_video: Optional[str] = None
    _just_completed_caption_preview: Optional[str] = None

    def to_progress_update(self) -> ProgressUpdate:
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0.0
        return ProgressUpdate(
            stage=self.stage,
            current_video=self.current_video,
            video_index=self.video_index,
            total_videos=self.total_videos,
            completed_videos=self.completed_videos,
            tokens_generated=self.tokens_generated,
            tokens_per_sec=self.tokens_per_sec,
            model_loaded=self.model_loaded,
            substage=self.substage,
            substage_progress=self.substage_progress,
            error_message=self.error_message,
            elapsed_time=elapsed,
            just_completed_video=self._just_completed_video,
            just_completed_caption_preview=self._just_completed_caption_preview,
        )


class ProcessingManager:
    """Manages video processing with real-time progress updates."""

    def __init__(self, progress_callback: Optional[Callable[[ProgressUpdate], Any]] = None):
        self.progress_callback = progress_callback
        self.model_info: Optional[Dict[str, Any]] = None
        self.should_stop = False
        self.is_processing = False
        self.state = ProcessingState()
        self._lock = asyncio.Lock()
        print("[ProcessingManager] Initialized")

    async def emit_progress(self):
        """Send current progress to callback"""
        if self.progress_callback:
            update = self.state.to_progress_update()
            if asyncio.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(update)
            else:
                self.progress_callback(update)
        # Clear transient completion event after sending
        self.state._just_completed_video = None
        self.state._just_completed_caption_preview = None

    def _get_display_name(self, video_path: Path) -> str:
        from backend import config as _config
        working_dir = _config.get_working_directory()
        try:
            return str(video_path.relative_to(working_dir)).replace('\\', '/')
        except ValueError:
            return video_path.name

    async def load_model(self, settings: Settings) -> bool:
        """
        Connect to the API server with the configured settings.
        Returns True on success, False on failure.
        """
        from backend.model_loader import load_model, clear_cache

        print(f"[ProcessingManager] load_model called, api_base_url={settings.api_base_url}")

        async with self._lock:
            try:
                self.state.stage = ProcessingStage.LOADING_MODEL
                self.state.substage = ProcessingSubstage.IDLE
                self.state.substage_progress = 0.0
                self.state.start_time = time.time()
                await self.emit_progress()

                if self.model_info is not None:
                    clear_cache()
                    self.model_info = None

                self.state.substage_progress = 0.1
                await self.emit_progress()

                loop = asyncio.get_event_loop()
                self.model_info = await loop.run_in_executor(
                    None,
                    lambda: load_model(model_id=settings.api_model_name)
                )

                self.state.model_loaded = True
                self.state.substage_progress = 1.0
                self.state.stage = ProcessingStage.IDLE
                await self.emit_progress()

                print(f"[ProcessingManager] Connected to {settings.api_base_url}, model: {settings.api_model_name}")
                return True

            except Exception as e:
                print(f"[ProcessingManager] Connection FAILED: {e}")
                import traceback
                traceback.print_exc()
                self.state.stage = ProcessingStage.ERROR
                self.state.error_message = str(e)
                self.state.model_loaded = False
                await self.emit_progress()
                return False

    async def process_videos(
        self,
        videos: List[Path],
        settings: Settings,
    ) -> List[Dict[str, Any]]:
        return await self._process_videos_sequential(videos, settings)

    async def _process_videos_sequential(
        self,
        videos: List[Path],
        settings: Settings,
    ) -> List[Dict[str, Any]]:
        from backend.model_loader import generate_caption
        from backend.video_processor import process_video, process_image
        from backend import config

        print(f"[ProcessingManager] Processing {len(videos)} files")

        if not self.state.model_loaded or self.model_info is None:
            success = await self.load_model(settings)
            if not success:
                return []

        async with self._lock:
            self.is_processing = True
            self.should_stop = False
            self.state.stage = ProcessingStage.PROCESSING
            self.state.total_videos = len(videos)
            self.state.video_index = 0
            self.state.completed_videos = 0
            self.state.start_time = time.time()
            await self.emit_progress()

            results = []
            loop = asyncio.get_event_loop()

            for i, video_path in enumerate(videos):
                if self.should_stop:
                    break

                self.state.video_index = i
                self.state.current_video = self._get_display_name(video_path)
                self.state.substage = ProcessingSubstage.EXTRACTING_FRAMES
                self.state.substage_progress = 0.0
                await self.emit_progress()

                result = {
                    "video": video_path.name,
                    "success": False,
                    "error": None,
                    "caption": None,
                }

                try:
                    self.state.substage_progress = 0.2
                    await self.emit_progress()

                    is_image = video_path.suffix.lower() in config.IMAGE_EXTENSIONS
                    if is_image:
                        frames, video_meta = await loop.run_in_executor(
                            None,
                            lambda: process_image(
                                video_path,
                                frame_size=settings.frame_size,
                            )
                        )
                    else:
                        frames, video_meta = await loop.run_in_executor(
                            None,
                            lambda: process_video(
                                video_path,
                                max_frames=settings.max_frames,
                                frame_size=settings.frame_size,
                            )
                        )

                    self.state.substage = ProcessingSubstage.ENCODING
                    self.state.substage_progress = 0.4
                    await self.emit_progress()

                    self.state.substage = ProcessingSubstage.GENERATING
                    self.state.substage_progress = 0.5
                    await self.emit_progress()

                    caption, gen_meta = await loop.run_in_executor(
                        None,
                        lambda: generate_caption(
                            model_info=self.model_info,
                            images=frames,
                            prompt=settings.prompt,
                            max_tokens=settings.max_tokens,
                            temperature=settings.temperature,
                            video_fps=video_meta.get("fps"),
                        )
                    )

                    self.state.tokens_generated += gen_meta["output_tokens"]
                    self.state.tokens_per_sec = gen_meta["tokens_per_sec"]

                    self.state.substage_progress = 0.9
                    await self.emit_progress()

                    output_path = video_path.parent / (video_path.stem + config.OUTPUT_EXTENSION)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(caption)
                        if settings.include_metadata:
                            f.write("\n\n" + "=" * 60 + "\n")
                            f.write("METADATA\n")
                            f.write("=" * 60 + "\n")
                            f.write(f"Video: {video_path.name}\n")
                            f.write(f"Frames processed: {gen_meta['num_frames']}\n")
                            f.write(f"Output tokens: {gen_meta['output_tokens']}\n")
                            f.write(f"Tokens/sec: {gen_meta['tokens_per_sec']:.1f}\n")

                    result["success"] = True
                    result["caption"] = caption[:200] + "..." if len(caption) > 200 else caption
                    result["output_path"] = str(output_path)

                    self.state.substage_progress = 1.0
                    self.state.completed_videos += 1
                    self.state._just_completed_video = self._get_display_name(video_path)
                    preview = caption[:150] + "..." if len(caption) > 150 else caption
                    self.state._just_completed_caption_preview = preview
                    await self.emit_progress()

                except Exception as e:
                    result["error"] = str(e)
                    self.state.error_message = f"Error processing {video_path.name}: {e}"
                    await self.emit_progress()

                results.append(result)

            self.state.stage = ProcessingStage.COMPLETE
            self.state.substage = ProcessingSubstage.IDLE
            self.state.current_video = None
            self.is_processing = False
            await self.emit_progress()

        return results

    def stop(self):
        self.should_stop = True

    def get_model_status(self) -> Dict[str, Any]:
        return {
            "loaded": self.state.model_loaded,
            "model_id": self.model_info.get("model_id") if self.model_info else None,
            "api_base_url": self.model_info.get("api_base_url") if self.model_info else None,
            "available_models": self.model_info.get("available_models", []) if self.model_info else [],
        }

    async def unload_model(self):
        from backend.model_loader import clear_cache

        async with self._lock:
            self.model_info = None
            self.state.model_loaded = False
            clear_cache()
            await self.emit_progress()
            print("[ProcessingManager] Disconnected from API server")

    def reset(self):
        self.state = ProcessingState()
        self.should_stop = False
        self.is_processing = False

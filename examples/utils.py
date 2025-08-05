from __future__ import annotations

import base64
from pathlib import Path

_SAMPLE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAIAAAAmkwkpAAAAEElEQVR4nGP8"
    "z4AATAxEcQAz0QEHOoQ+uAAAAABJRU5ErkJggg=="
)


def ensure_sample_image() -> Path:
    """Ensure the sample.png asset exists and return its path."""
    asset_dir = Path(__file__).resolve().parent / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    sample_path = asset_dir / "sample.png"
    if not sample_path.exists():
        sample_path.write_bytes(base64.b64decode(_SAMPLE_B64))
    return sample_path


def ensure_sample_video() -> Path:
    """Ensure a small sample.mp4 video exists and return its path."""
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        raise RuntimeError(
            "opencv-python and numpy are required for sample video"
        )

    asset_dir = Path(__file__).resolve().parent / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    video_path = asset_dir / "sample.mp4"
    if not video_path.exists():
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 2.0, (64, 64))
        for i in range(10):
            frame = np.zeros((64, 64, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                str(i),
                (5, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
            )
            out.write(frame)
        out.release()
    return video_path

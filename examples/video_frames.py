from __future__ import annotations

"""Extract frames from a video with Parslet."""

from pathlib import Path
from typing import List

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner

try:
    import cv2
except Exception as exc:  # noqa: broad-except
    cv2 = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


@parslet_task
def extract_frames(video_path: str, out_dir: str = "frames") -> List[Path]:
    """Save all frames from ``video_path`` to ``out_dir``."""
    if cv2 is None:
        raise ImportError("opencv-python is required") from IMPORT_ERROR
    cap = cv2.VideoCapture(video_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        fname = out / f"frame_{idx:03d}.png"
        cv2.imwrite(str(fname), frame)
        frames.append(fname)
        idx += 1
    cap.release()
    return frames


@parslet_task
def count_frames(frames: List[Path]) -> int:
    return len(frames)


def main(video_path: str) -> List[ParsletFuture]:
    frames = extract_frames(video_path)
    count = count_frames(frames)
    return [count]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main("video.mp4"))
    runner = DAGRunner()
    runner.run(dag)

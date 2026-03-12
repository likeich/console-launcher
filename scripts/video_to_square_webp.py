#!/usr/bin/env python3
"""Convert a video into a centered square animated WebP."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a centered 1:1 animated WebP from a video."
    )
    parser.add_argument("input", type=Path, help="Path to the source video.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .webp path. Defaults to the input filename with a .webp extension.",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=512,
        help="Square output size in pixels. Defaults to 512.",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=15,
        help="Output frame rate. Defaults to 15.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        parser.error("ffmpeg is required but was not found on PATH.")

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"Input file does not exist: {input_path}")

    if args.size <= 0:
        parser.error("--size must be a positive integer.")

    if args.fps <= 0:
        parser.error("--fps must be a positive integer.")

    output_path = (
        args.output.expanduser().resolve()
        if args.output
        else input_path.with_suffix(".webp")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vf = (
        f"fps={args.fps},"
        "crop='min(iw,ih)':'min(iw,ih)',"
        f"scale={args.size}:{args.size}:flags=lanczos"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        vf,
        "-loop",
        "0",
        "-an",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    print(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

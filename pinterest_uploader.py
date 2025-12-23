import argparse
import base64
import json
import os
from pathlib import Path
from typing import Dict, List

import requests


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_TRACK_FILE = Path(".posted_images.json")


class PinterestUploader:
    def __init__(
        self,
        images_dir: Path,
        board_id: str,
        access_token: str,
        track_file: Path = DEFAULT_TRACK_FILE,
        dry_run: bool = False,
    ) -> None:
        self.images_dir = images_dir
        self.board_id = board_id
        self.access_token = access_token
        self.track_file = track_file
        self.dry_run = dry_run
        self._posted = self._load_posted()

    def _load_posted(self) -> Dict[str, Dict[str, str]]:
        if not self.track_file.exists():
            return {}
        try:
            return json.loads(self.track_file.read_text())
        except json.JSONDecodeError:
            return {}

    def _save_posted(self) -> None:
        self.track_file.write_text(json.dumps(self._posted, indent=2))

    def _iter_images(self) -> List[Path]:
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")
        files = [
            path
            for path in sorted(self.images_dir.iterdir())
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        return files

    def _encode_image(self, path: Path) -> str:
        return base64.b64encode(path.read_bytes()).decode("utf-8")

    def _upload_image(self, path: Path) -> Dict:
        image_b64 = self._encode_image(path)
        payload = {
            "board_id": self.board_id,
            "title": path.stem.replace("_", " "),
            "media_source": {
                "source_type": "image_base64",
                "content_type": f"image/{path.suffix.lstrip('.').lower()}",
                "data": image_b64,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://api.pinterest.com/v5/pins",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def post_images(self, limit: int | None = None) -> List[Path]:
        posted_now: List[Path] = []
        for image_path in self._iter_images():
            if image_path.name in self._posted:
                continue
            if limit is not None and len(posted_now) >= limit:
                break

            if self.dry_run:
                print(f"[dry-run] Would post: {image_path}")
                self._posted[image_path.name] = {"pin_id": "dry-run"}
                posted_now.append(image_path)
                continue

            result = self._upload_image(image_path)
            pin_id = result.get("id") or result.get("pin_id") or "unknown"
            self._posted[image_path.name] = {"pin_id": pin_id}
            posted_now.append(image_path)
            print(f"Posted {image_path} -> pin {pin_id}")

        if posted_now:
            self._save_posted()
        return posted_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload local images to a Pinterest board."
    )
    parser.add_argument(
        "--images-dir",
        default="images",
        type=Path,
        help="Directory containing images to upload (default: images)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of images to post in this run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call Pinterest; just log what would happen.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    access_token = os.getenv("PINTEREST_ACCESS_TOKEN")
    board_id = os.getenv("PINTEREST_BOARD_ID")

    if not access_token:
        raise SystemExit("Missing PINTEREST_ACCESS_TOKEN environment variable.")
    if not board_id:
        raise SystemExit("Missing PINTEREST_BOARD_ID environment variable.")

    uploader = PinterestUploader(
        images_dir=args.images_dir,
        board_id=board_id,
        access_token=access_token,
        dry_run=args.dry_run,
    )
    posted = uploader.post_images(limit=args.limit)
    print(f"Uploaded {len(posted)} image(s).")


if __name__ == "__main__":
    main()

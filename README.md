# monkey-pinterest-images
Daily images for Pinterest auto-posting (MonkeyVibe).

## Pinterest upload helper

Use `pinterest_uploader.py` to send new images from `./images` to a Pinterest board.

1. Create a Pinterest app token and set environment variables:
   - `PINTEREST_ACCESS_TOKEN`: OAuth access token with pin create scope.
   - `PINTEREST_BOARD_ID`: Target board ID (e.g., `1234567890123`).
2. Run the uploader:
   ```bash
   python pinterest_uploader.py --limit 3
   # or dry-run to preview without posting
   python pinterest_uploader.py --dry-run
   ```

Notes:
- Only new files are posted; posted filenames are tracked in `.posted_images.json`.
- Supported formats: jpg, jpeg, png, webp.

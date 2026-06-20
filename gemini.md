# AI Session Context: IG Reels Automation Bot

**Purpose:** This file provides immediate context for any new AI session interacting with this codebase.

## 1. Design & Algorithmic Directives
- **Theme:** AI, Automation, and Everyday Tech Productivity.
- **Metric Optimization:** The bot is highly optimized for Instagram "Saves" and Watch Time (Loops). Hooks are designed to be "Save-bait" and captions are extremely long tutorials with an "AUTOMATE" comment Call-To-Action.
- **Voice:** `edge-tts` using `en-US-GuyNeural` (Professional, fast-paced male voice). Rate is boosted by `+25%` to keep audience attention.
- **Subtitles:** English only (center, Arial-Bold, lowercase/natural casing). Background overlay is darkened to 0.55 for a sleek dark-mode aesthetic.

## 2. Technical Architecture
- **Text & Translation:** Gemini 2.5 Flash (`src/quote_generator.py` and `src/video_assembler.py`).
- **Transcription:** `faster-whisper` (CPU mode, int8 compute). Output is phrase-level, not word-level.
- **Video Sourcing:** Pexels API (`src/video_sourcer.py`). Queries match the friendship theme.
- **Assembly:** `moviepy` and ImageMagick (`src/video_assembler.py`).

## 3. Strict Development Constraints
1. **Font Paths (CRITICAL):** Do not break the cross-platform font logic in `video_assembler.py`. Windows uses `C:\Windows\Fonts\msyh.ttc`, Linux (DigitalOcean) uses `WenQuanYi-Zen-Hei`.
2. **Environment Variables:** `GEMINI_API_KEY`, `PEXELS_API_KEY`, `IG_USER_ID`, `IG_ACCESS_TOKEN`. These live in `.env` which is strictly `.gitignore`'d. Do not ever commit them.
3. **Large Files:** All generated `.mp4`, `.mp3`, and `.m4a` files are ignored in Git.

## 4. Deployment Environment
- **Host:** DigitalOcean Droplet (Ubuntu).
- **Execution:** Runs via standard cron.
- **Dependency Quirk:** The server requires `sudo apt-get install fonts-wqy-zenhei` for ImageMagick to successfully render the Chinese text.


import html
import os
import re
import tempfile

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def clean_vtt_text(vtt_content: str) -> str:
    """Convert WebVTT captions into readable text and remove rolling overlap."""

    cues = re.split(r"\n\s*\n", vtt_content.strip())
    transcript_words = []

    for cue in cues:
        lines = cue.strip().splitlines()

        # Find the caption timing line.
        timing_index = next(
            (i for i, line in enumerate(lines) if "-->" in line),
            None,
        )

        if timing_index is None:
            continue

        cue_text = " ".join(lines[timing_index + 1:])

        # Remove inline timestamps and formatting tags.
        cue_text = re.sub(
            r"<\d{2}:\d{2}:\d{2}\.\d{3}>",
            "",
            cue_text,
        )
        cue_text = re.sub(r"<[^>]*>", "", cue_text)

        # Decode HTML entities.
        cue_text = html.unescape(cue_text)
        cue_text = re.sub(r"\s+", " ", cue_text).strip()

        if not cue_text:
            continue

        words = cue_text.split()

        # Remove overlapping words from rolling YouTube captions.
        max_overlap = min(len(transcript_words), len(words), 50)
        overlap = 0

        for size in range(max_overlap, 0, -1):
            previous = [
                re.sub(r"[^\w]", "", word).lower()
                for word in transcript_words[-size:]
            ]

            current = [
                re.sub(r"[^\w]", "", word).lower()
                for word in words[:size]
            ]

            if previous == current:
                overlap = size
                break

        transcript_words.extend(words[overlap:])

    return " ".join(transcript_words).strip()


def download_yt_transcript(url: str, language: str = "english"):
    """
    Download English YouTube captions without downloading audio.

    Returns transcript text when successful.
    Returns None when captions are unavailable or retrieval fails.
    """

    if language.lower() != "english":
        print("Transcript-first currently supports English captions only.")
        return None

    try:
        print("\n========== YOUTUBE TRANSCRIPT STARTED ==========")

        # Fetch video metadata and available caption tracks.
        with yt_dlp.YoutubeDL(
            {"quiet": True, "no_warnings": True}
        ) as ydl:

            info = ydl.extract_info(url, download=False)

        manual = info.get("subtitles") or {}
        automatic = info.get("automatic_captions") or {}

        def find_english_code(captions):
            if "en" in captions:
                return "en"

            return next(
                (
                    code
                    for code in captions
                    if code.lower().startswith("en-")
                ),
                None,
            )

        manual_code = find_english_code(manual)
        automatic_code = find_english_code(automatic)

        # Prefer manually uploaded captions.
        if manual_code:
            selected_code = manual_code
            use_automatic = False

            print(f"Using manual captions: {selected_code}")

        elif automatic_code:
            selected_code = automatic_code
            use_automatic = True

            print(f"Using automatic captions: {selected_code}")

        else:
            print("No English captions available.")
            return None

        # Use a temporary directory so subtitle files don't accumulate.
        with tempfile.TemporaryDirectory() as temp_dir:

            output_template = os.path.join(
                temp_dir,
                "%(id)s.%(language)s.%(ext)s",
            )

            subtitle_options = {
                "skip_download": True,
                "writesubtitles": not use_automatic,
                "writeautomaticsub": use_automatic,
                "subtitleslangs": [selected_code],
                "subtitlesformat": "vtt/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(subtitle_options) as ydl:
                ydl.download([url])

            vtt_files = [
                os.path.join(temp_dir, filename)
                for filename in os.listdir(temp_dir)
                if filename.lower().endswith(".vtt")
            ]

            if not vtt_files:
                print("No VTT subtitle file was generated.")
                return None

            with open(
                vtt_files[0],
                "r",
                encoding="utf-8",
            ) as file:

                transcript = clean_vtt_text(file.read())

        if not transcript:
            print("Transcript was empty after cleaning.")
            return None

        print(
            f"Transcript downloaded successfully: "
            f"{len(transcript.split())} words"
        )

        print("========== YOUTUBE TRANSCRIPT SUCCESS ==========\n")

        return transcript

    except Exception as e:
        print(
            f"Transcript retrieval failed: {type(e).__name__}: {e}"
        )

        print("Will attempt audio + Whisper fallback.")

        return None


def download_yt_audio(url: str) -> str:
    print("\n========== YOUTUBE DOWNLOAD STARTED ==========")
    print(f"Input URL: {url}")

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s",
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": False,
        "verbose": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            print("[1/3] Extracting video information...")

            info = ydl.extract_info(url, download=False)

            print(f"Video title: {info.get('title')}")
            print(f"Video ID: {info.get('id')}")
            print(f"Duration: {info.get('duration')} seconds")

            print("[2/3] Downloading audio...")

            info = ydl.extract_info(url, download=True)

            print("[3/3] Preparing WAV filename...")

            filename = os.path.splitext(
                ydl.prepare_filename(info)
            )[0] + ".wav"

            print(f"Download completed: {filename}")
            print("========== DOWNLOAD SUCCESS ==========\n")

            return filename

    except Exception as e:
        print("\n========== YOUTUBE DOWNLOAD FAILED ==========")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print("============================================\n")

        raise


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format."""

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 5) -> list:
    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):

        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:

    if source.startswith("https://") or source.startswith("http://"):

        print("Detected YouTube URL, downloading audio...")

        wav_path = download_yt_audio(source)

    else:

        print("Detected local file, converting to WAV...")

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready - {len(chunks)} chunk(s) created")

    return chunks

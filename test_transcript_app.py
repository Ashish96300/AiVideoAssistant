
import streamlit as st
import yt_dlp
import os

st.title("YouTube Transcript Cloud Test")

video_url = st.text_input(
    "YouTube URL",
    "https://youtu.be/3lAvZJ14zSo?si=wjzIs1JmH7MowpB8"
)

if st.button("Test YouTube Captions"):
    try:
        st.write("1. Connecting to YouTube...")

        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(video_url, download=False)

        st.success("Metadata request successful!")
        st.write("Title:", info.get("title"))

        manual = info.get("subtitles", {})
        automatic = info.get("automatic_captions", {})

        st.write("Manual captions:", list(manual.keys()))
        st.write("Automatic captions:", list(automatic.keys()))

        if not manual and not automatic:
            st.warning("No captions available.")
        else:
            st.write("2. Attempting subtitle download...")

            os.makedirs("test_transcripts", exist_ok=True)

            options = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en", "en-US", "en-GB"],
                "subtitlesformat": "vtt/best",
                "outtmpl": "test_transcripts/%(id)s.%(ext)s",
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([video_url])

            files = os.listdir("test_transcripts")

            if files:
                st.success("Subtitle download successful!")
                st.write("Generated files:", files)

                for file in files:
                    if file.endswith(".vtt"):
                        with open(
                            os.path.join("test_transcripts", file),
                            encoding="utf-8"
                        ) as f:
                            st.text_area(
                                "Transcript preview",
                                f.read()[:5000],
                                height=250
                            )
            else:
                st.warning("No subtitle file was generated.")

    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")

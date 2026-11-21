import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)


# def download_yt_audio(url : str)->str:
#     output_path = os.path.join(DOWNLOAD_DIR , "%(title)s.%(ext)s")
#     ydl_opts={
#         "format":"bestaudio/best",
#         "outtmpl":output_path,
#         "postprocessors":[{
#             "key":"FFmpegExtractAudio",
#             "preferredcodec":"wav",
#             "preferredquality":"192",
#         }],
#         "quiet":True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url,download=True)
#         filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"
#     return filename 

def download_yt_audio(url: str) -> str:
    print("\n========== YOUTUBE DOWNLOAD STARTED ==========")
    print(f"Input URL: {url}")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

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

# data = download_yt_audio('https://youtu.be/lgDjJ-FO824?si=PSk3tHvColJqWd9w')

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path

# converted_wav = convert_to_wav(data)

def chunk_audio(wav_path:str , chunk_minutes:int=5)->list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes*60*1000

    chunks =[]

    for i,start in enumerate(range(0 , len(audio) , chunk_ms)):
        chunk = audio[start : start+chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format ="wav")

        chunks.append(chunk_path)

    return chunks

# chunk_audio(converted_wav)

def process_input(source:str)->list:
    if source.startswith('https://') or source.startswith("http://"):
        print("Detected yt url , downloading audo...")
        wav_path = download_yt_audio(source)
    else:
        print("dected local file .converting to wav...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready -{len(chunks)} chunk(s) created")
    return chunks

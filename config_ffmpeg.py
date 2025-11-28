import os

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"

os.environ["PATH"] = os.environ.get("PATH", "") + ";" + os.path.dirname(FFMPEG_PATH)
os.environ["FFMPEG"] = FFMPEG_PATH
os.environ["FFPROBE"] = FFPROBE_PATH

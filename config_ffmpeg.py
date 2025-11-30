import os
import platform

if platform.system() == "Windows":
    FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
    FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"
else:
    FFMPEG_PATH = "ffmpeg"
    FFPROBE_PATH = "ffprobe"

os.environ["PATH"] = os.environ.get("PATH", "") + ";" + os.path.dirname(FFMPEG_PATH)
os.environ["FFMPEG"] = FFMPEG_PATH
os.environ["FFPROBE"] = FFPROBE_PATH

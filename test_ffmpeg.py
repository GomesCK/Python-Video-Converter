import subprocess
from config_ffmpeg import *

try:
    out = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT, text=True)
    print(out)
except Exception as e:
    print("ERRO:", e)

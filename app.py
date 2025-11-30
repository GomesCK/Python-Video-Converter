# app.py
from flask import Flask, request, send_file, jsonify, render_template
# import os
import uuid
import yt_dlp
import subprocess
from config_ffmpeg import *   # define caminhos FFMPEG_PATH e FFPROBE_PATH e adiciona ao PATH

app = Flask(__name__, static_folder="static", template_folder="templates")

OUTPUT_DIR = "converted"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    link = data.get("url")
    fmt = data.get("format", "mp3")

    if not link:
        return jsonify({"error": "URL não informada"}), 400

    try:
        uid = str(uuid.uuid4())
        temp_output = f"temp_{uid}.%(ext)s"

        # Opções do yt-dlp: força local do ffmpeg para evitar WinError 2
        ydl_opts = {
            "ffmpeg_location": os.path.dirname(FFMPEG_PATH) if "FFMPEG_PATH" in globals() else r"C:\ffmpeg\bin",
            "outtmpl": temp_output,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Achar arquivo baixado
        downloaded_file = None
        for f in os.listdir("."):
            if f.startswith(f"temp_{uid}"):
                downloaded_file = f
                break

        if not downloaded_file:
            return jsonify({"error": "Não foi possível baixar o vídeo."}), 500

        output_filename = f"video_{uid}.{fmt}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Caminho explícito pro ffmpeg
        ffmpeg_exec = FFMPEG_PATH if "FFMPEG_PATH" in globals() else r"C:\ffmpeg\bin\ffmpeg.exe"

        # Converter: chamando o ffmpeg diretamente para não depender do PATH do processo
        if fmt == "mp3":
            cmd = [
                ffmpeg_exec,
                "-i", downloaded_file,
                "-vn",
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                output_path,
                "-y"
            ]
        elif fmt == "mp4":
            cmd = [
                ffmpeg_exec,
                "-i", downloaded_file,
                "-vcodec", "libx264",
                "-acodec", "aac",
                "-pix_fmt", "yuv420p",
                output_path,
                "-y"
            ]
        else:
            return jsonify({"error": "Formato inválido"}), 400

        # Executa ffmpeg e captura erros
        subprocess.run(cmd, check=True)

        # Remove arquivo temporário
        try:
            os.remove(downloaded_file)
        except Exception:
            pass

        # Envia o arquivo convertido como download — o frontend acompanha o progresso do download
        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as sp_err:
        print("ERRO ffmpeg:", sp_err)
        return jsonify({"error": "Erro na conversão (ffmpeg). Veja logs do servidor."}), 500
    except Exception as e:
        print("ERRO:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

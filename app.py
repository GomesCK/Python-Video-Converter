from flask import Flask, request, send_file, jsonify, render_template
import uuid
import yt_dlp
import subprocess
import os
import sys

from config_ffmpeg import *   # FFMPEG_PATH e FFPROBE_PATH

app = Flask(__name__, static_folder="static", template_folder="templates")
COOKIE_FILE = "www.youtube.com_cookies.txt"

OUTPUT_DIR = "converted"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)



# ==========================================================
# TENTA CARREGAR COOKIES DO NAVEGADOR
# ==========================================================

def get_cookie_file():
    if os.path.exists(COOKIE_FILE):
        return COOKIE_FILE
    return None

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    link = data.get("url")
    fmt = data.get("format", "mp3")

    if not link:
        return jsonify({"error": "Nenhuma URL recebida"}), 400

    try:
        uid = str(uuid.uuid4())
        temp_output = f"temp_{uid}.%(ext)s"

        # Detectar cookies localmente
        cookies = get_cookie_file()

        ydl_opts = {
            "outtmpl": temp_output,
            "quiet": True,
            "ffmpeg_location": os.path.dirname(FFMPEG_PATH),
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        # Se tiver cookies, habilita
        if cookies:
            ydl_opts["cookiefile"] = cookies
        else:
            print("\n⚠️ Nenhum cookie encontrado — vídeos protegidos pelo YouTube podem falhar.\n")

        # ------------------------------
        # DOWNLOAD
        # ------------------------------
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # encontra arquivo baixado
        downloaded_file = next((f for f in os.listdir(".") if f.startswith(f"temp_{uid}")), None)
        if not downloaded_file:
            return jsonify({"error": "Falha ao baixar o vídeo."}), 500

        output_filename = f"video_{uid}.{fmt}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        ffmpeg_exec = FFMPEG_PATH

        # ------------------------------
        # CONVERSÃO
        # ------------------------------
        if fmt == "mp3":
            cmd = [
                ffmpeg_exec, "-i", downloaded_file, "-vn",
                "-acodec", "libmp3lame", "-b:a", "192k",
                output_path, "-y"
            ]
        elif fmt == "mp4":
            cmd = [
                ffmpeg_exec, "-i", downloaded_file,
                "-vcodec", "libx264", "-acodec", "aac",
                "-pix_fmt", "yuv420p",
                output_path, "-y"
            ]
        else:
            return jsonify({"error": "Formato inválido"}), 400

        subprocess.run(cmd, check=True)

        # remove temporário
        try:
            os.remove(downloaded_file)
        except:
            pass

        return send_file(output_path, as_attachment=True)

    except yt_dlp.utils.DownloadError as download_err:
        err = str(download_err)

        # mensagem clara pra cookie
        if "Sign in to confirm" in err or "confirm you’re not a bot" in err:
            return jsonify({
                "error": (
                    "Este vídeo precisa de autenticação. "
                    "Abra o YouTube no navegador e permaneça logado, "
                    "depois tente novamente."
                )
            }), 403

        return jsonify({"error": err}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

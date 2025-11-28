import subprocess
import sys
import os
import webbrowser
import time
import socket

def find_open_port(start=5000):
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1

def get_python_exec():
    # Quando empacotado no PyInstaller
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "python.exe")
    # Modo desenvolvimento
    return sys.executable

def get_app_path():
    base = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "app.py")

def wait_for_server(port, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except:
            time.sleep(0.2)
    return False

if __name__ == "__main__":
    port = find_open_port(5000)
    python_exec = get_python_exec()
    app_path = get_app_path()

    # Inicia o Flask corretamente
    subprocess.Popen([python_exec, app_path], env={**os.environ, "FLASK_PORT": str(port)})

    # Espera o servidor realmente iniciar
    if wait_for_server(port):
        webbrowser.open(f"http://127.0.0.1:{port}")
    else:
        pass  # ou um pop-up dizendo "falhou"

    while True:
        time.sleep(1)

# import threading
# import webbrowser
# import time
# import subprocess
# import sys
# import os
#
# def start_flask():
#     # Garante que o Flask rode no mesmo diretório do EXE
#     base_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))
#     app_path = os.path.join(base_dir, "app.py")
#
#     # Starta o servidor
#     subprocess.Popen([sys.executable, app_path])
#
# # ===============================
# # INÍCIO DO APP
# # ===============================
# if __name__ == "__main__":
#     # Inicia Flask em segundo plano
#     t = threading.Thread(target=start_flask, daemon=True)
#     t.start()
#
#     # Espera o servidor iniciar
#     time.sleep(2)
#
#     # Abre só UMA aba
#     # webbrowser.open("http://127.0.0.1:5000")
#
#     # Mantém o EXE vivo
#     print("Servidor rodando. Feche a janela para encerrar.")
#     while True:
#         time.sleep(1)

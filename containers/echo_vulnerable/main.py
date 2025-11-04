from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import sys

PORT = 8002
HOST = "192.168.1.12"


class EchoHandler(BaseHTTPRequestHandler):
    """
    Este handler processa requisições GET e POST.
    """

    # Silencia os logs de requisição no console para não poluir
    def log_message(self, format, *args):
        pass

    def _send_json_response(self, status_code, data):
        """Helper para enviar respostas JSON."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        """Trata requisições GET."""
        if self.path == "/":
            self._send_json_response(
                200,
                {
                    "message": "Bem-vindo à API de Echo! Use o endpoint /echo para testar."
                },
            )
        else:
            self._send_json_response(404, {"error": "Not Found"})

    def do_POST(self):
        """Trata requisições POST."""
        if self.path == "/echo":
            try:
                # 1. Obter o tamanho do corpo da requisição
                content_length = int(self.headers["Content-Length"])

                # 2. Ler o corpo da requisição
                post_data = self.rfile.read(content_length)

                # 3. Decodificar e parsear o JSON
                body_json = json.loads(post_data.decode("utf-8"))

                message = body_json.get("message")

                if message is not None:
                    # 4. Enviar a resposta de echo
                    self._send_json_response(200, {"echo": message})
                else:
                    self._send_json_response(400, {"error": "Campo 'message' ausente."})

            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "JSON mal formatado."})
            except Exception as e:
                self._send_json_response(500, {"error": str(e)})
        else:
            self._send_json_response(404, {"error": "Not Found"})


class ThreadingEchoServer(ThreadingMixIn, HTTPServer):
    """
    Este é o servidor que usa uma thread por conexão.
    ThreadingMixIn: Garante que cada requisição seja tratada em uma nova thread.
    """

    daemon_threads = True  # Permite encerrar o servidor com Ctrl+C


if __name__ == "__main__":
    try:
        server_address = (HOST, PORT)
        httpd = ThreadingEchoServer(server_address, EchoHandler)

        print(f"--- Servidor Vulnerável ao Slowloris Iniciado ---")
        print(f"Escutando em http://{HOST}:{PORT}")
        print("Este servidor usa uma thread por conexão.")
        print("Pressione Ctrl+C para encerrar.")

        httpd.serve_forever()

    except OSError as e:
        if e.errno == 98:  # Erro "Address already in use"
            print(f"\n❌ ERRO: A porta {PORT} já está em uso.")
            print("Verifique se outro servidor (talvez o FastAPI) está rodando.")
        elif e.errno == 99:  # Erro "Cannot assign requested address"
            print(f"\n❌ ERRO: Não foi possível se vincular ao IP {HOST}.")
            print("Verifique se o IP está correto ou tente usar '0.0.0.0'.")
        else:
            print(f"\n❌ ERRO: {e}")

    except KeyboardInterrupt:
        print("\n👋 Encerrando o servidor...")
        httpd.server_close()
        sys.exit(0)

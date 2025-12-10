import requests
import random
import time

SERVER_URL = "http://192.168.1.10:8001/scrape"
STARTING_URL = "https://pt.wikipedia.org/wiki/Unix"

MIN_DELAY_SECONDS = 30
MAX_DELAY_SECONDS = 120


def run_infinite_scraper_client():
    current_url = STARTING_URL
    hop_count = 0

    print("--- Iniciando Cliente Scraper (Modo Resiliente) ---")
    print(f"URL inicial: {current_url}\n")

    try:
        while True:
            hop_count += 1
            print(f"--- [ Salto {hop_count} ] ---")
            print(f"Enviando requisição para: {current_url}")

            payload = {"url": current_url}

            try:
                # Enviamos a requisição ao nosso servidor API
                response = requests.post(SERVER_URL, json=payload, timeout=20)

                # Se o servidor responder com erro (4xx ou 5xx), isso levanta exceção
                response.raise_for_status()

                data = response.json()
                found_urls = data.get("found_urls")

                # Caso de "Beco sem saída" (página sem links)
                if not found_urls:
                    print(
                        "🚫 Fim da linha (sem links nesta página). Voltando ao início..."
                    )
                    current_url = STARTING_URL
                    hop_count = 0  # Opcional: reiniciar contagem
                    time.sleep(5)
                    continue

                # Fluxo normal: escolhe proximo link
                current_url = random.choice(found_urls)
                print(f"✅ Sucesso! {len(found_urls)} URLs encontradas.")
                print(f"Próximo destino: {current_url}")

                random_delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"Aguardando {random_delay:.1f}s...\n")
                time.sleep(random_delay)

            # --- TRATAMENTO DE ERROS PARA REINICIAR ---
            except requests.exceptions.HTTPError as e:
                # O servidor respondeu, mas com código de erro (ex: a url alvo estava quebrada)
                error_msg = "Erro desconhecido"
                try:
                    error_msg = response.json().get("detail")
                except:
                    error_msg = e.response.text

                print(f"⚠️ O servidor retornou um erro: {error_msg}")
                print(f"🔄 Reiniciando rota a partir de: {STARTING_URL}\n")

                current_url = STARTING_URL
                hop_count = 0
                time.sleep(5)  # Pequena pausa de segurança antes de reiniciar

            except requests.exceptions.RequestException as e:
                # Erro de conexão (o servidor da API caiu ou rede falhou)
                print(f"❌ Erro de conexão com a API: {e}")
                print("Tentando reconectar em 10 segundos...")
                time.sleep(10)
                # Neste caso, mantemos a current_url para tentar de novo,
                # ou você pode resetar para STARTING_URL se preferir.

    except KeyboardInterrupt:
        print("\n👋 Encerrando cliente.")


if __name__ == "__main__":
    run_infinite_scraper_client()

import requests
import random
import time

SERVER_URL = "http://192.168.1.10:8001/scrape"
STARTING_URL = "https://pt.wikipedia.org/wiki/Unix"

MIN_DELAY_SECONDS = 30
MAX_DELAY_SECONDS = 90


def run_infinite_scraper_client():
    """
    Executa o cliente que interage com a API de scraping em um loop infinito,
    escolhendo a próxima URL aleatoriamente e aguardando um tempo
    aleatório entre as requisições.
    """
    current_url = STARTING_URL
    hop_count = 0

    print("--- Iniciando Cliente Scraper (Modo Infinito) ---")
    print(">>> Pressione Ctrl+C para encerrar a qualquer momento. <<<")
    print(f"URL inicial: {current_url}\n")

    try:
        while True:
            hop_count += 1
            print(f"--- [ Salto {hop_count} ] ---")
            print(f"Enviando requisição para: {current_url}")

            payload = {"url": current_url}

            try:
                response = requests.post(SERVER_URL, json=payload, timeout=20)
                response.raise_for_status()

                data = response.json()
                found_urls = data.get("found_urls")

                if not found_urls:
                    print(
                        "Fim da linha! Nenhuma URL foi encontrada nesta página. Encerrando."
                    )
                    break

                current_url = random.choice(found_urls)

                print(f"✅ Sucesso! {len(found_urls)} URLs encontradas.")
                print(f"Próximo destino escolhido aleatoriamente: {current_url}")

                random_delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)

                print(
                    f"Aguardando por {random_delay:.1f} segundos antes do próximo salto...\n"
                )

                time.sleep(random_delay)

            except requests.exceptions.HTTPError as e:
                print(
                    f"❌ Erro do servidor: {e.response.status_code} - {e.response.text}"
                )
                print("Encerrando devido a erro do servidor.")
                break

            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão com o servidor: {e}")
                print("Encerrando devido a erro de conexão.")
                break

    except KeyboardInterrupt:
        print("\n\n👋 Encerrando o cliente por solicitação do usuário. Até mais!")

    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

    finally:
        print("--- Cliente Scraper Finalizado ---")


if __name__ == "__main__":
    run_infinite_scraper_client()

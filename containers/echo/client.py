import requests
import random
import time
import string

SERVER_URL = "http://192.168.1.11:8000/echo"

MIN_DELAY_SECONDS = 2 * 60  # 2 minutos
MAX_DELAY_SECONDS = 5 * 60  # 10 minutos

MIN_MSG_LENGTH = 256
MAX_MSG_LENGTH = 4096


def generate_random_string(length: int) -> str:
    """
    Gera uma string aleatória com letras, dígitos e pontuação.
    """
    characters = (
        string.ascii_letters + string.digits + string.punctuation + " " * 10
    )  # Adiciona mais espaços
    return "".join(random.choice(characters) for i in range(length))


def run_echo_client():
    """
    Executa um cliente que envia mensagens aleatórias para o servidor de echo
    em intervalos de tempo aleatórios.
    """
    print("--- Iniciando Cliente de Echo (Modo Infinito) ---")
    print(">>> Pressione Ctrl+C para encerrar a qualquer momento. <<<")

    try:
        while True:
            # 1. Gera uma mensagem com tamanho aleatório
            message_length = random.randint(MIN_MSG_LENGTH, MAX_MSG_LENGTH)
            random_message = generate_random_string(message_length)

            payload = {"message": random_message}

            print(f"Enviando mensagem com {message_length} caracteres...")

            try:
                response = requests.post(SERVER_URL, json=payload, timeout=30)
                response.raise_for_status()

                response_data = response.json()
                echoed_message = response_data.get("echo", "")

                print(
                    f"✅ Sucesso! O servidor ecoou uma mensagem de {len(echoed_message)} caracteres."
                )

            except requests.exceptions.HTTPError as e:
                print(
                    f"❌ Erro do servidor: {e.response.status_code} - {e.response.text}"
                )
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão com o servidor: {e}")

            # 4. Calcula o próximo delay e aguarda
            delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
            minutes, seconds = divmod(delay, 60)
            print(
                f"Próxima requisição em {int(minutes)} minutos e {int(seconds)} segundos.\n"
            )
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n\n👋 Encerrando o cliente por solicitação do usuário. Até mais!")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        print("--- Cliente de Echo Finalizado ---")


if __name__ == "__main__":
    run_echo_client()

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class ScrapeRequest(BaseModel):
    url: HttpUrl


app = FastAPI(
    title="Simple Scraper API",
    description="Uma API HTTP para extrair links de páginas web.",
)


def scrape_links(url: str):
    """
    Tenta baixar e extrair links. Se falhar, a exceção é propagada
    para ser tratada pelo endpoint.
    """
    print(f"Iniciando scrape da URL: {url}")

    # Define um User-Agent para evitar bloqueios simples (403)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # O timeout pode gerar exceção, o requests.get pode gerar exceção
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Levanta erro se status for 4xx ou 5xx

    soup = BeautifulSoup(response.content, "lxml")
    found_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue

        absolute_url = urljoin(url, href)
        # Filtro opcional: garantir que é http/https
        if absolute_url.startswith("http"):
            found_urls.add(absolute_url)

    print(f"Encontradas {len(found_urls)} URLs.")
    return list(found_urls)


@app.post("/scrape")
async def create_scrape_request(request: ScrapeRequest):
    """
    Recebe uma URL. Se ocorrer erro no scrape, retorna HTTP 400 com detalhe.
    """
    try:
        found_urls = scrape_links(str(request.url))

        # Se a página carregar mas não tiver links, retornamos lista vazia (sucesso)
        return {"source_url": str(request.url), "found_urls": found_urls}

    except Exception as e:
        # Aqui capturamos o erro e enviamos ao cliente
        error_msg = f"Falha ao processar URL: {str(e)}"
        print(f"❌ Erro enviado ao cliente: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


@app.get("/")
def read_root():
    return {"message": "Servidor Scraper está no ar."}


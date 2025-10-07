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
    Baixa o conteúdo de uma URL, analisa o HTML e extrai todos os links (href).
    Converte links relativos em absolutos.
    """
    print(f"Iniciando scrape da URL: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")

        found_urls = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href or href.startswith("#"):
                continue

            absolute_url = urljoin(url, href)
            found_urls.add(absolute_url)

        print(f"Encontradas {len(found_urls)} URLs.")
        return list(found_urls)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL {url}: {e}")
        raise HTTPException(
            status_code=400, detail=f"Não foi possível acessar a URL: {e}"
        )

    except Exception as e:
        print(f"Erro inesperado no scrape: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro inesperado no servidor."
        )


@app.post("/scrape")
async def create_scrape_request(request: ScrapeRequest):
    """
    Recebe uma URL, faz o scraping dos links e retorna a lista de URLs encontradas.
    """
    found_urls = scrape_links(str(request.url))

    return {"source_url": str(request.url), "found_urls": found_urls}


@app.get("/")
def read_root():
    return {
        "message": "Servidor Scraper está no ar. Use o endpoint POST /scrape para iniciar."
    }

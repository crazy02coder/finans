from urllib.parse import quote

from bs4 import BeautifulSoup
from curl_cffi import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI(title="Yahoo Finance Quote API")

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


class QuoteError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def get_quote(ticker: str) -> dict:
    """Yahoo Finance sayfasından fiyat ve istatistikleri çeker."""
    ticker = ticker.strip().upper()

    if not ticker:
        raise QuoteError("Ticker boş olamaz.", 400)

    url = f"https://finance.yahoo.com/quote/{quote(ticker, safe='')}/"

    try:
        response = requests.get(
            url,
            impersonate="chrome124",
            headers=HEADERS,
            timeout=15,
        )
    except requests.exceptions.Timeout as exc:
        raise QuoteError("Yahoo Finance isteği zaman aşımına uğradı.", 504) from exc
    except requests.exceptions.RequestException as exc:
        raise QuoteError(f"Yahoo Finance bağlantı hatası: {exc}", 502) from exc
    except Exception as exc:
        raise QuoteError(f"Veri alınırken beklenmeyen bir hata oluştu: {exc}", 502) from exc

    if response.status_code in (403, 429):
        raise QuoteError(
            f"Yahoo Finance isteği engelledi (HTTP {response.status_code}).",
            503,
        )

    if response.status_code == 404:
        raise QuoteError(f"'{ticker}' ticker'ı Yahoo Finance'ta bulunamadı.", 404)

    if response.status_code != 200:
        raise QuoteError(
            f"Yahoo Finance beklenmeyen bir yanıt döndürdü (HTTP {response.status_code}).",
            502,
        )

    soup = BeautifulSoup(response.text, "html.parser")

    price_tag = soup.select_one('[data-testid="qsp-price"]')
    if price_tag is None:
        raise QuoteError(
            "Fiyat alanı bulunamadı; Yahoo Finance sayfa yapısı değişmiş olabilir.",
            502,
        )

    stats_container = soup.select_one('[data-testid="quote-statistics"]')
    if stats_container is None:
        raise QuoteError(
            "İstatistik alanı bulunamadı; Yahoo Finance sayfa yapısı değişmiş olabilir.",
            502,
        )

    stats = {}
    for item in stats_container.select("li"):
        spans = item.find_all("span")
        if len(spans) >= 2:
            label = spans[0].get_text(strip=True)
            value = spans[-1].get_text(strip=True)
            if label:
                stats[label] = value

    if not stats:
        raise QuoteError(
            "İstatistikler parse edilemedi; Yahoo Finance sayfa yapısı değişmiş olabilir.",
            502,
        )

    return {
        "ticker": ticker,
        "price": price_tag.get_text(strip=True),
        "stats": stats,
    }


@app.get("/")
def root() -> dict:
    return {"message": "Yahoo Finance Quote API", "example": "/quote/NVDA"}


@app.get("/quote/{ticker}")
def quote_endpoint(ticker: str):
    try:
        return get_quote(ticker)
    except QuoteError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

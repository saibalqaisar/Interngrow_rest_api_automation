"""Web scraping with BeautifulSoup (practice site made for scraping)."""
from bs4 import BeautifulSoup
from utils import safe_get, log

URL = "https://quotes.toscrape.com/"


def scrape_quotes(limit=5):
    resp = safe_get(URL)
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    quotes = []
    for block in soup.select("div.quote")[:limit]:
        quotes.append({
            "text": block.select_one("span.text").get_text(strip=True),
            "author": block.select_one("small.author").get_text(strip=True),
        })
    log.info("Scraped %s quotes", len(quotes))
    return quotes

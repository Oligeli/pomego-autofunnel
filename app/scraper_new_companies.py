import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Company

ORSR_NEW_URL = "https://www.orsr.sk/hladaj_vznik.asp"


# -------------------------------
# ASYNC časť — Playwright scraping
# -------------------------------
async def scrape_orsr_new():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(ORSR_NEW_URL, wait_until="load")
        html = await page.content()

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tbody tr")

        db: Session = SessionLocal()
        added = 0

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 5:
                continue

            name = cols[0]
            ico = cols[1]
            city = cols[3]

            # Skontrolujeme, či firma už existuje (ako placeholder uložíme ICO do website)
            existing = db.query(Company).filter(Company.website == ico).first()
            if existing:
                continue

            company = Company(
                name=name,
                website=ico,  # dočasne ukladáme ICO
                email=None,
                phone=None,
                address=city,
                segment="new_company",
                status="new",
                lead_score=0,
            )

            db.add(company)
            added += 1

        db.commit()
        db.close()

        await browser.close()

        print(f"[SCRAPER] Added {added} new companies.")
        return added


# ---------------------------------------------------
# SYNC funkcia — volateľná z API aj z workeru
# ---------------------------------------------------
def run_scraper():
    print("[SCRAPER] Starting ORSR new companies scraper...")

    try:
        # Získame aktuálny event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Ak loop už beží (Render + FastAPI)
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(scrape_orsr_new(), loop)
            added = future.result()
        else:
            added = loop.run_until_complete(scrape_orsr_new())

        return {"added": added}

    except Exception as e:
        print("[SCRAPER] Error:", e)
        return {"error": str(e)}


# ---------------------------------------------------
# Lokálne spustenie manuálne
# ---------------------------------------------------
if __name__ == "__main__":
    print(run_scraper())

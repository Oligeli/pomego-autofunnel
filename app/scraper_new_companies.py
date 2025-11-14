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

            # Check if already exists
            existing = db.query(Company).filter(Company.website == ico).first()
            if existing:
                continue

            company = Company(
                name=name,
                website=ico,         # temporarily use ICO in website column
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
        added = asyncio.run(scrape_orsr_new())
        return {"added": added}
    except Exception as e:
        print("[SCRAPER] Error:", e)
        return {"error": str(e)}


# Pre lokálne testovanie
if __name__ == "__main__":
    print(run_scraper())

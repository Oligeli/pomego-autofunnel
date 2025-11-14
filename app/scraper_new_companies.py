import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Company
import datetime

ORSR_URL = "https://www.orsr.sk/hladaj_ico.asp?lan=sk"

async def fetch_html(page, url):
    await page.goto(url, wait_until="load")
    return await page.content()

async def scrape_new_firms():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Stranka s novými firmami
        url = "https://www.orsr.sk/hladaj_vznik.asp"
        html = await fetch_html(page, url)

        soup = BeautifulSoup(html, "html.parser")

        # Tabuľka obsahuje nové zápisy
        rows = soup.select("table tbody tr")

        db: Session = SessionLocal()

        added = 0

        for row in rows:
            cols = [c.text.strip() for c in row.find_all("td")]
            if len(cols) < 5:
                continue

            name = cols[0]
            ico = cols[1]
            city = cols[3]
            date = cols[4]

            # Skontrolujeme či už existuje v DB
            existing = db.query(Company).filter(Company.website == ico).first()
            if existing:
                continue

            company = Company(
                name=name,
                website=None,
                email=None,
                phone=None,
                address=city,
                segment="new_company",
                status="new",
                lead_score=0
            )

            db.add(company)
            added += 1

        db.commit()
        db.close()
        print(f"Added {added} new companies.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_new_firms())

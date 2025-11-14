from fastapi import FastAPI
from app.scraper_new_companies import run_scraper

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/run-scraper")
def manual_run():
    result = run_scraper()
    return {"status": "scraper_started", "result": result}

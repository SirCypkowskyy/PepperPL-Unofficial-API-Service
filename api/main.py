import json
from fastapi import FastAPI

from scraper import DatabaseScraperService

app = FastAPI(
    title="Pepper.pl Unofficial API",
    description="Unofficial API for Pepper.pl",
    version="0.1.0"
)


@app.get("/")
async def root():
    """
    Basic Root endpoint
    :return: JSON connection confirmation
    """
    return {"message": "Hi, you are using Pepper.pl unofficial API!"}


@app.get("/get/all")
async def get_all():
    """
    Endpoint for getting all deals
    :return: JSON with all deals from all registered categories
    """
    with open("../data/deals.json", "r", encoding="utf-8") as f:
        json_file_contents = json.load(f)
        return json_file_contents


@app.get("/get/category/{category}")
async def get_category(category: str):
    """
    Endpoint for getting deals from specific category
    :param category: Category name (use name from URL address)
    :return: JSON with all deals from specific category
    """
    with open("../data/deals.json", "r", encoding="utf-8") as f:
        json_file_contents = json.load(f)
        if json_file_contents["categories"][category] is not None:
            return json_file_contents["categories"][category]
        else:
            return {"message": "Category not found"}


@app.on_event("startup")
async def run_scheduler():
    database_scraper_service = DatabaseScraperService(5, False)
    await database_scraper_service.start()

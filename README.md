<p align="center">
    <img src="logo.png" width="150">
</p>


# Pepper.pl unofficial API service

This is a simple API service for the [Pepper.pl](https://pepper.pl) website, based on page data scraping. It is not affiliated with the website or its creators in any way.

## Contents
* [Introduction](#introduction)
* [Installation](#installation)
* [Available calls](#available-calls)
* [Roadmap](#roadmap)
* [Final remarks](#final-remarks)
## Introduction

This program is a simple Python script that runs in the background and periodically checks the pepper.pl website for new posts to scrap. It then stores the posts in a database and serves them through a simple API service (FastAPI).

**For your assurance, be warned:
I take no responsibility for the use of the API and do not guarantee its performance or that I will continue to develop it in the future.**
## Installation
Instructions on how to install `poetry` can be found [here](https://python-poetry.org/docs/#installation).

Set up your virtual environment and install the dependencies:
```bash
poetry install
```
Run `main.py` from `/api/` folder to start the API service. It will automatically create a data file in new "data" folder. The API will be available at http://127.0.0.1:8000.
## Available calls
At the moment, following calls are available:
* `/` - returns a JSON connection confirmation
* `/get/all` - returns a JSON with all posts
* `/get/{category}` - returns a JSON with posts from a given category
## Roadmap
* [ ] Add support for conditional requests (by price, merchant, discount rates, etc.)
* [ ] More API endpoints
* [ ] More scraped data per post (e.g. post author, post date, post sub-category, etc.)
* [ ] Full-time working website
## Final remarks
The operation of the program may change due to changes in the code of the site or the very libraries used to write this program.

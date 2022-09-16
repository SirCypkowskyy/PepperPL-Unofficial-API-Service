import datetime
import json
import os.path
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler


PEPPER_PL_WEBSITE = "https://www.pepper.pl/"


class DatabaseScraperService:
    def __init__(self):
        self.sch = None
        self.queue = None

    async def update_json_file(self, show_debug=False):
        """
        Function for updating deals.json data file
        """
        print("Commencing update of JSON data file...")
        did_accept_cookies = False
        options = Options()
        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        bot = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Scraping started...")
        with open("../data/checked_categories.txt", "r", encoding="utf-8") as checked_categories_file:
            checked_categories = checked_categories_file.read().splitlines()

        with open("../data/deals.json", "r", encoding="utf-8") as f:
            json_file_contents = json.load(f)
        for category in checked_categories:
            json_file_contents["categories"][category] = []
            for i in range(1, 5):
                bot.get(f"{PEPPER_PL_WEBSITE}grupa/{category}?page={i}")
                if not did_accept_cookies:
                    sleep(1)
                    btns = bot.find_element(By.XPATH,
                                            '//*[@id="main"]/div[4]/div[1]/div/div/div/div[2]/div[2]/button[1]/span')
                    btns.click()
                    did_accept_cookies = True
                    sleep(0.5)
                for j in range(1, 4):
                    sleep(0.2)
                    bot.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                content = bot.page_source
                soup = BeautifulSoup(content, 'html.parser')
                articles = soup.find_all("article")
                for article in articles[:20]:
                    title = article.find("a", {"class": "cept-tt"})
                    if title is not None:
                        if title["href"] is not None:
                            deal_link = title["href"]
                        else:
                            deal_link = ""
                        title = title.text
                    else:
                        title = "No title"
                        deal_link = ""

                    org_price = article.find("span", {"class": "mute--text"})
                    if org_price is not None:
                        org_price = org_price.text
                    else:
                        org_price = "No price"
                    new_price = article.find("span", {"class": "thread-price"})
                    if new_price is not None:
                        new_price = new_price.text
                        if "ZA DARMO" in new_price:
                            new_price = "0"
                    else:
                        new_price = "No price"
                    discount_rate = article.find("span", {"class": "space--ml-1"})
                    if discount_rate is not None:
                        discount_rate = discount_rate.text
                    else:
                        discount_rate = "No discount"

                    merchant = article.find("span", {"class": "cept-merchant-name"})
                    if merchant is not None:
                        merchant = merchant.text
                    else:
                        merchant = "No merchant"

                    is_expired = (article.find("span", {"class": "cept-show-expired-threads"}) is not None)
                    img = article.find("img")["src"]
                    description = article.find("div", {"class": "userHtml-content"})
                    if description is not None:
                        description = description.text
                    else:
                        description = "No description"

                    # TODO: FIX EXPIRED_AT SPAN (currently it's returning new_price value)

                    expires_at = article.find("span", {"class": "hide--toW3"})
                    if expires_at is not None:
                        expires_at = expires_at.text
                        expires_at = expires_at.replace("Obowiązuje do ", "")
                    else:
                        expires_at = "No expiration date"
                    if show_debug:
                        print(
                            f"title: {title}\n"
                            f"description: {description}\n"
                            f"deal_link: {deal_link}\n"
                            f"original_price: {org_price}\n"
                            f"new_price: {new_price}\n"
                            f"discount_rate: {discount_rate}\n"
                            f"merchant: {merchant}\n"
                            f"is_expired: {is_expired}\n"
                            f"image: {img}\n"
                            f"expires_at: {expires_at}\n"
                        )
                    if not is_expired and title != "No title":
                        dict_to_append = {
                            "title": title,
                            "description": description,
                            "deal_link": deal_link,
                            "original_price": org_price,
                            "new_price": new_price,
                            "discount_rate": discount_rate,
                            "merchant": merchant,
                            "is_expired": is_expired,
                            "image": img,
                            "expires_at": expires_at
                        }
                        json_file_contents["categories"][category].append(dict_to_append)

            print(f"{category} scraped successfully!")
        json_file_contents["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("../data/deals.json", "w", encoding="utf-8") as f:
            json.dump(json_file_contents, f, indent=4)
        bot.close()
        print("Done scraping!")

    async def start(self):
        """
        Function for starting the service
        """
        print("Starting the service...")
        if not os.path.exists("../data"):
            os.makedirs("../data")
        if not os.path.exists("../data/deals.json"):
            with open("../data/deals.json", "w", encoding="utf-8") as f:
                json.dump({"categories": {}, "last_updated": ""}, f, indent=4)

        if not os.path.exists("../data/checked_categories.txt"):
            with open("../data/checked_categories.txt", "w", encoding="utf-8") as f:
                f.write("gry\nelektronika\ndom-i-mieszkanie\nmoda\ndom\nzdrowie-i-uroda\ndla-dzieci\nartykuly"
                        "-spozywcze\npodroze\nmotoryzacja\nrozrywka\nsport\nuslugi-i-subskrypcje")

        self.queue = asyncio.Queue()
        self.sch = AsyncIOScheduler()
        await self.update_json_file()
        self.sch.start()
        self.sch.add_job(self.update_json_file,
                         "interval",
                         minutes=5,
                         max_instances=1)




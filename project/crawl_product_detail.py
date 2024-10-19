import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
import json

# Constants
FILE_PATH = "/home/kiet/Downloads/data_name_error.csv"
FILE_URL_ERROR = "url_error.txt"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "glamira"
COLLECTION_NAME = "fix_name"
MAX_CONCURRENT_REQUESTS = 20  # Số lượng yêu cầu đồng thời tối đa

async def insert_mongo_db(client, product_id, name, url):
    db = client[DB_NAME]
    target_collection = db[COLLECTION_NAME]
    document = {
        '_id': product_id,
        'product_name': name,
        'current_url': url
    }
    try:
        await target_collection.insert_one(document)
    except Exception as e:
        print(f"Error inserting document into MongoDB: {e}")

async def fetch_url(session, url, product_id):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        async with session.get(url) as response:
            print(f"Status: {response.status}, URL: {response.url}")
            if response.status == 200 and "checkout/cart" not in str(response.url):
                return await response.text(), str(response.url)
            else:
                print(f"Failed to fetch {url} with status: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Error connecting to {url}: {e}")
    return None, url


async def process_content(content, product_id, url, client):
    soup = BeautifulSoup(content, "html.parser")
    name = None
    # Try different methods to find the product name
    methods = [
        lambda: soup.find('span', class_='base').text,
        lambda: next((span.text for infor in soup.find_all("div", class_=["info_stone", "info_stone_total"])
                      for product_item_detail in [soup.find("h2", class_=["product-item-details", "product-name"])]
                      for span in [product_item_detail.find("span", "hide-on-mobile")]
                      if json.loads(infor.find("p", class_=["enable-popover", "popover_stone_info"])["data-ajax-data"]).get("product_id") == product_id), None),
        lambda: soup.find("div", class_="product-info-desc").find("h1").text
    ]
    for method in methods:
        try:
            name = method()
            if name:
                break
        except AttributeError:
            continue
    if name:
        await insert_mongo_db(client, product_id, name, url)
    else:
        print(f"No product name found for {url}")

async def process_row(semaphore, session, row, mongo_client):
    product_id, url = row[0], row[1].strip()
    if not url or url == "current_url":
        print(f"Invalid URL: {url}")
        return
    
    async with semaphore:  # Sử dụng semaphore để giới hạn số lượng yêu cầu đồng thời
        content, final_url = await fetch_url(session, url, product_id)
        if content:
            await process_content(content, product_id, final_url, mongo_client)
        else:
            with open(FILE_URL_ERROR, 'a', newline='') as error_file:
                error_writer = csv.writer(error_file)
                error_writer.writerow([url])
    
        await asyncio.sleep(5)  # Thêm thời gian chờ 10 giây giữa các yêu cầu

async def main():
    client = AsyncIOMotorClient(MONGO_URI)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)  # Khởi tạo semaphore
    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            with open(FILE_PATH, mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    tg.create_task(process_row(semaphore, session, row, client))

if __name__ == "__main__":
    asyncio.run(main())

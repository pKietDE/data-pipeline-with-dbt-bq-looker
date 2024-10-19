import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import random
from urllib.parse import urlencode, urlparse, urlunparse
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# URL của trang web
url = "https://www.glamira.com/"
header = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"}

# Config Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Tập hợp để theo dõi các URL đã xử lý
processed_urls = set()

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def make_request(url, session=None):
    if session is None:
        session = create_session()
    
    try:
        time.sleep(random.uniform(1, 3))
        response = session.get(url, headers=header, timeout=30)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi khi tải URL {url}: {str(e)}")
        return None

def main():
    session = create_session()
    res = make_request(url, session)
    if not res:
        return
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    top_menu = soup.find_all("li", class_="tablinks")

    for item in top_menu:
        href = item.find("a").get("href")
        handle_in_top_link(href, session)

def handle_in_top_link(url, session):
    if url in processed_urls:
        logging.info(f"Đã xử lý: {url}")
        return

    res = make_request(url, session)
    if not res:
        return
        
    soup = BeautifulSoup(res.text, "html.parser")
    processed_urls.add(url)

    if url == "https://www.glamira.com/fashion-lp/":
        logging.info(f"Bỏ qua link {url}")
    elif url == "https://www.glamira.com/jewelry/":
        logging.info(f"Xử lý link {url}")
        handle_link_jewelry(soup, session)
    elif url == "https://www.glamira.com/engagement-rings/":
        logging.info(f"Xử lý link {url}")
        handle_link_engagement(soup, session)

def handle_link_jewelry(soup, session):
    list_url = []
    tag_a = soup.find_all("a", class_="pagebuilder-button-link")
    if tag_a:
        for a in tag_a[2:-4]:
            href = a.get("href")
            list_url.append(href)

    handle_image(list_url, session)

def handle_link_engagement(soup, session):
    list_url = []
    li = soup.find_all("li", class_="menuitem--parent")

    for item in li[10:-9]:
        link = item.find("a")
        if link:
            href = link.get("href")
            list_url.append(href)

    handle_image(list_url, session)

def handle_image(list_url, session):
    for url in list_url:
        res = make_request(url, session)
        if not res:
            continue
            
        soup = BeautifulSoup(res.text, "html.parser")

        total_item = soup.find("span", class_="result-interlligent-search")
        
        if total_item and total_item.text:
            total_products = 0
            page = 1
            while total_products < int(total_item.text):
                current_url = url if page == 1 else f"{url}?p={page}"
                    
                total_product_crawled = handle_image_page(current_url, page, int(total_item.text), session)
                
                if total_product_crawled == 0:
                    logging.warning(f"Không lấy được sản phẩm nào từ trang {page}, chuyển sang URL tiếp theo")
                    break

                total_products += total_product_crawled
                logging.info(f"Đã crawl {total_products} sản phẩm từ trang {page}. Tổng sản phẩm còn lại: {int(total_item.text) - total_products}.")
                
                page += 1
        else:
            logging.warning(f"Không tìm thấy thông tin về tổng số sản phẩm trên trang {url}")

def handle_image_page(url, page, total_item, session):
    res = make_request(url, session)
    if not res:
        return 0
        
    soup = BeautifulSoup(res.text, "html.parser")
    li = soup.find_all("li", class_=f"item-page-{page}")
    
    processed_items = 0
    for item in li:
        try:
            product_id = None
            product_name = None
            href = None
            src = None
            data_params_dic = {}

            tag_a = item.find("a", class_=["product-link","img-product"])
            p = item.find("p", class_=["enable-popover","popover_stone_info"])
            h2 = item.find("h2", class_=["product-item-details","product-name"])  

            if h2:
                product_name = h2.text.strip()
            else:
                logging.warning("Không tìm thấy product_name")

            if tag_a:
                href = tag_a.get("href")
                img = tag_a.find("img", class_="product-image-photo")
                if img:
                    src = img.get("src")
                else:
                    logging.warning("Không tìm thấy img")
            else:
                logging.warning("Không tìm thấy thẻ tag_a")

            if p:
                data_ajax_data = p.get("data-ajax-data")
                data = json.loads(data_ajax_data) if data_ajax_data else {}
                product_id = data.get("product_id")
                
                if product_id is not None:
                    data_params_dic.update({"product_id": product_id})

            if href:
                current_url = build_full_url(href, data_params_dic)
                insert_data_in_mongo(product_id, product_name, current_url, src, url)
                processed_items += 1

        except Exception as e:
            logging.error(f"Lỗi khi xử lý sản phẩm: {str(e)}")
            continue

    return processed_items

def build_full_url(href, data_params_dic):
    parsed_url = urlparse(href)
    query = urlencode(data_params_dic)
    return urlunparse(parsed_url._replace(query=query))

def insert_data_in_mongo(product_id, product_name, product_link, product_image, product_url):
    try:
        client = MongoClient("mongodb://localhost:27017", 
                           serverSelectionTimeoutMS=60000,
                           connectTimeoutMS=60000,
                           socketTimeoutMS=60000)
        db = client["glamira"]
        target_collection = db["image_raw_full"]

        document = {
            "product_id": product_id,
            "product_name": product_name,
            "product_link": product_link,
            "product_image": product_image,
            "product_current_url": product_url,
        }

        target_collection.insert_one(document)
        client.close()
    except Exception as e:
        logging.error(f"Lỗi khi lưu vào MongoDB: {str(e)}")

if __name__ == "__main__":
    main()
from asyncio import exceptions
import functions_framework
from google.cloud import bigquery
from google.cloud import storage
import json
import datetime
import os

# Set up BigQuery and Storage clients
storage_client = storage.Client()

# Replace these variables with your information
DATASET_ID = "final_project"
TABLE_ID = "ip_locations"
TABLE_ID_PRODUCT = "product_informations"
TABLE_ID_GLAMIRA = "glamira_raw"
TABLE_ID_CART_PRODUCTS = "cart_products"  # New table for cart products
TABLE_ID_OPTION = "options"  # New table for options

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    bucket = data["bucket"]
    name = data["name"]

    print(f"Processing file: {name}")

    try:
        if "ip" in name:
            insert_ip_bq(bucket, name)
        elif "product" in name:
            insert_product_bq(bucket, name)
        else:
            process_file(bucket, name)
    except Exception as e:
        print(f"Error processing file {name}: {str(e)}")
        raise

def process_file(bucket_name, file_name):
    try:
        # Khởi tạo clients
        storage_client = storage.Client()
        bigquery_client = bigquery.Client()

        # Tải file từ GCS
        print(f"Đang tải file {file_name} từ bucket {bucket_name}")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        json_data = blob.download_as_text()
        
        # Parse JSON
        print("Đang phân tích dữ liệu JSON...")
        data = json.loads(json_data)
        print(f"Tìm thấy {len(data)} bản ghi")

        # Transform data
        transformed_data = transform_data(data)

        # Định nghĩa job config
        job_config = bigquery.LoadJobConfig(
            schema=get_table_schema(),
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        table_id = os.getenv('BIGQUERY_TABLE_ID', 'optimum-archery-434816-e4.dec_project2.glamira_raw')
        
        # Upload to BigQuery
        print(f"Bắt đầu tải dữ liệu lên BigQuery cho bảng: {table_id}")
        job = bigquery_client.load_table_from_json(
            transformed_data,
            table_id,
            job_config=job_config
        )

        # Wait for job to complete
        job.result()  # Raises an exception if job fails
        print(f"Đã tải thành công {len(transformed_data)} dòng vào {table_id}")

    except exceptions.BadRequest as e:
        print(f"Lỗi BadRequest khi tải dữ liệu lên BigQuery: {e}")
        for error in job.errors:
            print(f"Lỗi chi tiết: {error['message']}")
        raise
    except Exception as e:
        print(f"Lỗi không mong đợi trong hàm process_file: {str(e)}")
        raise

def transform_data(data):
    """Transform raw data into BigQuery compatible format"""
    transformed = []
    for item in data:
        transformed_item = {
            'event_id': str(item.get('_id', {}).get('$oid', '')),
            'time_stamp': process_timestamp(item.get('time_stamp')),
            'ip': item.get('ip', ''),
            'user_agent': item.get('user_agent', ''),
            'resolution': item.get('resolution', ''),
            'user_id_db': item.get('user_id_db', ''),
            'device_id': item.get('device_id', ''),
            'api_version': float(item.get('api_version', 0)),
            'store_id': item.get('store_id', ''),
            'local_time': process_local_time(item.get('local_time', '')),
            'show_recommendation': process_boolean(item.get('show_recommendation')),
            'current_url': item.get('current_url', ''),
            'referrer_url': item.get('referrer_url', ''),
            'email_address': item.get('email_address', ''),
            'collection': item.get('collection', ''),
            'product_id': item.get('product_id', ''),
            'price': process_price(item.get('price')),
            'currency': item.get('currency', ''),
            'order_id': process_order_id(item.get('order_id')),
            'is_paypal': process_boolean(item.get('is_paypal')),
            'viewing_product_id': item.get('viewing_product_id', ''),
            'options': process_options(item.get('option')),
            'cart_products': process_cart_products(item.get('cart_products', [])),
            'recommendation': process_boolean(item.get('recommendation')) if 'recommendation' in item else None,
            'utm_source': process_boolean(item.get('utm_source')),
            'utm_medium': process_boolean(item.get('utm_medium'))
        }
        transformed.append(transformed_item)
    return transformed

def process_timestamp(timestamp):
    if timestamp is None:
        return None
    try:
        return int(timestamp)
    except ValueError:
        print(f"Timestamp không hợp lệ: {timestamp}")
        return None

def process_local_time(local_time):
    if not local_time:
        return None
    try:
        return datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S").isoformat()
    except ValueError:
        print(f"Định dạng local_time không hợp lệ: {local_time}")
        return None

def process_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == 'true'
    return None

def process_price(price_str):
    if price_str is None:
        return None
    try:
        price_str = price_str.replace(',', '').replace('.', '')
        price_str = ''.join(filter(str.isdigit, price_str))
        return int(price_str) if price_str else None
    except ValueError:
        print(f"Không thể xử lý giá trị price: {price_str}")
        return None

def process_order_id(order_id):
    try:
        return int(order_id) if order_id else None
    except ValueError:
        print(f"Không thể xử lý order_id: {order_id}")
        return None

def process_options(options):
    if not options:
        return []
    if isinstance(options, dict):
        options = [options]
    return [
        {
            'option_label': opt.get('option_label'),
            'value_label': opt.get('value_label'),
            'value_id': process_value_id(opt.get('value_id')),
            'quality': opt.get('quality'),
            'quality_label': opt.get('quality_label'),
            'alloy': opt.get('alloy'),
            'diamond': opt.get('diamond'),
            'shapediamond': opt.get('shapediamond')
        } for opt in options
    ]

def process_value_id(value_id):
    if isinstance(value_id, int):
        return value_id
    elif isinstance(value_id, str):
        return int(value_id) if value_id.isdigit() else None
    else:
        return None

def process_cart_products(cart_products):
    if not isinstance(cart_products, list):
        print(f"cart_products không phải là list: {cart_products}")
        return []
    
    return [
        {
            'product_id': str(product.get('product_id', '')),
            'amount': product.get('amount'),
            'price': process_price(product.get('price', '0')),
            'currency': product.get('currency', ''),
            'options': process_options(product.get('option', []))
        } for product in cart_products
    ]

def get_table_schema():
    """Return BigQuery table schema"""
    return [
        bigquery.SchemaField("event_id", "STRING"),
        bigquery.SchemaField("time_stamp", "INTEGER"),
        bigquery.SchemaField("ip", "STRING"),
        bigquery.SchemaField("user_agent", "STRING"),
        bigquery.SchemaField("resolution", "STRING"),
        bigquery.SchemaField("user_id_db", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("device_id", "STRING"),
        bigquery.SchemaField("api_version", "FLOAT"),
        bigquery.SchemaField("store_id", "STRING"),
        bigquery.SchemaField("local_time", "TIMESTAMP"),
        bigquery.SchemaField("show_recommendation", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("current_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("referrer_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("email_address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("collection", "STRING"),
        bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("price", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("order_id", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("is_paypal", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("viewing_product_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("options", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("option_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("value_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("value_id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("quality", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("quality_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("alloy", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("diamond", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("shapediamond", "STRING", mode="NULLABLE"),
        ]),
        bigquery.SchemaField("cart_products", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("product_id", "STRING"),
            bigquery.SchemaField("amount", "INTEGER"),
            bigquery.SchemaField("price", "INTEGER"),
            bigquery.SchemaField("currency", "STRING"),
            bigquery.SchemaField("options", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("option_label", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("value_label", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("value_id", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("quality", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("quality_label", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("alloy", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("diamond", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("shapediamond", "STRING", mode="NULLABLE"),
            ]),
        ]),
        bigquery.SchemaField("recommendation", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("utm_source", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("utm_medium", "BOOLEAN", mode="NULLABLE"),
    ]
def insert_ip_bq(bucket, filename):
    client = bigquery.Client()
    schema = [
        bigquery.SchemaField("ip", "STRING"),
        bigquery.SchemaField("country_short", "STRING"),
        bigquery.SchemaField("country_long", "STRING"),
        bigquery.SchemaField("region", "STRING"),
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("longtitude", "FLOAT"),
        bigquery.SchemaField("latitude", "FLOAT"),
        bigquery.SchemaField("zip_code", "STRING"),
        bigquery.SchemaField("timezone", "STRING"),
    ]

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=schema,
    )

    source_uri = f"gs://{bucket}/{filename}"

    try:
        job = client.load_table_from_uri(source_uri, f"{DATASET_ID}.{TABLE_ID}", job_config=job_config)
        job.result()
        print(f"Loaded {job.output_rows} rows into {DATASET_ID}:{TABLE_ID}.")
    except Exception as e:
        print(f"Failed to load IP data into BigQuery: {str(e)}")
        raise

def insert_product_bq(bucket, filename):
    client = bigquery.Client()
    schema = [
        bigquery.SchemaField("_id", "STRING"),
        bigquery.SchemaField("product_name", "STRING"),
        bigquery.SchemaField("product_image", "STRING", mode="REPEATED"),
        bigquery.SchemaField("current_url", "STRING"),
        bigquery.SchemaField("view_click", "STRING"),
    ]

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
    )

    source_uri = f"gs://{bucket}/{filename}"

    try:
        job = client.load_table_from_uri(source_uri, f"{DATASET_ID}.{TABLE_ID_PRODUCT}", job_config=job_config)
        job.result()
        print(f"Loaded {job.output_rows} rows into {DATASET_ID}:{TABLE_ID_PRODUCT}.")
    except Exception as e:
        print(f"Failed to load product data into BigQuery: {str(e)}")
        raise

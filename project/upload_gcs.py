import time
import os
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core import retry

# Thiết lập thông tin
local_folder = "/mnt/backup/data/json/glamira_full_raw/"  # Thư mục cục bộ chứa các file cần tải lên
bucket_name = "bkt-full-glamira"  # Tên bucket trên GCS
destination_folder = ""  # Để trống nếu muốn tải thẳng lên bucket mà không có thư mục
interval_minutes = 5  # Cài đặt thời gian nghỉ (5 phút)
skip_files = []  # Các file bỏ qua

# Lấy đường dẫn đến file JSON chứa thông tin xác thực từ biến môi trường
credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

def get_storage_client():
    """Tạo và trả về một storage client."""
    if credentials_path:
        # Nếu có đường dẫn đến file credentials, sử dụng nó
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return storage.Client(credentials=credentials)
    else:
        # Nếu không có file credentials, sử dụng xác thực mặc định
        return storage.Client()

@retry.Retry()
def upload_to_gcs(local_file_path, bucket_name, destination_blob_name):
    """Tải file lên GCS với khả năng retry."""
    try:
        # Kết nối tới GCS
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Tải file lên
        blob.upload_from_filename(local_file_path)
        print(f"File {local_file_path} đã được tải lên {bucket_name}/{destination_blob_name}.")
    except Exception as e:
        print(f"Lỗi khi tải file {local_file_path}: {str(e)}")
        raise  # Raise lại exception để retry mechanism có thể xử lý

def upload_files_once():
    """Tải file lên GCS theo thứ tự và dừng lại sau khi hoàn thành."""
    try:
        # Lấy danh sách tất cả các file trong thư mục cục bộ
        all_files = os.listdir(local_folder)
        
        # Sắp xếp các file theo thứ tự
        sorted_files = sorted(all_files)
        
        for filename in sorted_files:
            local_file_path = os.path.join(local_folder, filename)
            
            # Kiểm tra nếu file nằm trong danh sách cần bỏ qua
            if filename in skip_files:
                print(f"File {filename} đã bị bỏ qua.")
                continue
            
            if os.path.isfile(local_file_path):
                # Tạo đường dẫn đích trên GCS
                destination_blob_name = os.path.join(destination_folder, filename)
                
                # Tải file lên GCS
                upload_to_gcs(local_file_path, bucket_name, destination_blob_name)
                
                # Nghỉ 5 phút trước khi tải file tiếp theo (trừ file cuối cùng)
                if filename != sorted_files[-1]:
                    print(f"Chờ {interval_minutes} phút trước khi tải file tiếp theo...")
                    time.sleep(interval_minutes * 60)
        
        print("Đã hoàn thành việc tải lên tất cả các file.")
    except Exception as e:
        print(f"Lỗi trong quá trình tải lên: {str(e)}")

# Gọi hàm để bắt đầu tải lên
if __name__ == "__main__":
    print("Bắt đầu quá trình tải lên...")
    upload_files_once()
    print("Quá trình tải lên đã kết thúc.")
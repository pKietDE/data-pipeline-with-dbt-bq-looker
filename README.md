# Dự án Extract Dữ liệu từ trang Glamira

Dự án này thực hiện việc trích xuất dữ liệu từ trang web Glamira và lưu trữ thông tin sản phẩm vào cơ sở dữ liệu MongoDB.

## Mục lục

- [Tổng quan](#tổng-quan)
- [Yêu cầu](#yêu-cầu)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Cấu hình](#cấu-hình)
- [luồng dữ liệu](#luồng-dữ-liệu)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Đóng góp](#đóng-góp)
- [Hình ảnh](#hình-ảnh)

## Tổng quan

Dự án này sử dụng Python để crawl dữ liệu từ trang web Glamira, xử lý thông tin sản phẩm và lưu trữ vào MongoDB. Quá trình này bao gồm việc duyệt qua các danh mục sản phẩm, trích xuất thông tin chi tiết và xử lý dữ liệu.
Từ những dữ liệu đã được crawl chúng ta sẽ cùng với nó và DBT để xử lý transform dữ liệu với 41tr bản ghi thô về hành vi của người dùng , và sau đó sử dụng looker để trực quan hóa dữ liệu.

## Yêu cầu

Để chạy dự án này, bạn cần cài đặt các thư viện sau:

- requests
- beautifulsoup4
- pymongo
- urllib3
- dbt
- dbt-bigquery

Tải file IP2Loc : ![link tải](https://lite.ip2location.com/database/db11-ip-country-region-city-latitude-longitude-zipcode-timezone)

## Cài đặt

1. Clone repository:
2. Di chuyển vào thư mục dự án:
3. Cài đặt các thư viện cần thiết:

## Sử dụng

Để chạy script, sử dụng lệnh sau:
+ python3 crawl_image_glamira.py # Script này sẽ crawl dữ liệu từ trang Glamira và lưu vào MongoDB.
+ python3 crawl_product_detail.py #Script này sẽ crawl tên sản phẩm đã được lọc theo product_id trong 41 triệu bản ghi
+ Tạo cloud function trên GCP : - [Xem chi tiết](#Cài-đặt-cloud-function) 
+ python3 upload_gcs.py # Script này sẽ export dữ liệu từ MongoDB và upload lên GCS. # Lưu ý ! phải tạo cloud function thì hàm nay mới hoạt động đúng mục đích 

## Cấu hình
1. Cấu hình Google Cloud:
- Đảm bảo bạn đã cài đặt và cấu hình Google Cloud SDK
- Thiết lập biến môi trường GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'
+ vào service account => chọn project sử dụng => tabs key => create new key => json

## Cài đặt coud function 
+ Vào GCP (Đăng nhập / Đăng ký credit để dùng thử) -> Search + Cloud run functions -> Create functions
-> Chọn trigger type : Cloud Storage -> Event type : Finalized -> Tiếp theo -> chọn phiên bản python
-> coppy code của file gcf_config.py -> thêm các thư viện trong file requirements.txt bên dưới comment cloud
-> deploy .
  
**Đối với Linux**
+ vào bashrc => thêm vào cuối dòng => export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json' => Lưu file => source ./bashrc

## Luồng dữ liệu
1. Crawl dữ liệu từ Glamira -> MongoDB
2. Export từ MongoDB -> Google Cloud Storage -> Cloud function -> Bigquery
3. Xử lý dữ liệu bằng DBT trên BigQuery
4. Hiển thị kết quả trên Looker


## Cấu trúc dự án
<pre>
<code>
project/
│
├── <span style="color: #4CAF50;">crawl_image_glamira.py</span>   # Script chính để crawl dữ liệu.
├── <span style="color: #4CAF50;">crawl_product_detail.py</span>  # Script chính để crawl chi tiết sản phẩm .
├── <span style="color: #4CAF50;">upload_gcs.py</span>            # Script để upload các thư mục đã export từ MongoDB.
├── <span style="color: #FFC107;">data_image.csv</span>           # Data chứa ảnh của sản phẩm.
├── <span style="color: #FFC107;">ip_location_full.csv</span>     # Data chứa vị trí của người dùng dựa vào ip .
├── <span style="color: #FFC107;">requirements.txt</span>         # Danh sách các thư viện cần thiết.
├── <span style="color: #2196F3;">gcf_config.py</span>            # File để cấu hình gg cloud functions trên gcp .
├── <span style="color: #2196F3;">README.md</span>                # File này.

dbt-server/ #Folder chứa dự án dbt
│
├── <span style="color: #4CAF50;">...</span>   # Vào file README để xem chi tiết
├── <span style="color: #4CAF50;">README.md</span>   # file hướng dẫn cách sử dụng dbt-server
├── <span style="color: #4CAF50;">dbt_project.yml</span>   # file cấu hình chính của một dự án DBT.
├── <span style="color: #4CAF50;">package-lock.yml</span>   # file liên quan đến việc khóa phiên bản của các gói mà dự án phụ thuộc vào, để đảm bảo rằng tất cả các thành viên trong nhóm đều sử dụng cùng một phiên bản của các thư viện và các dependency không bị thay đổi bất ngờ khi cài đặt lại.
├── <span style="color: #4CAF50;">packages.yml</span>   # file để quản lý các gói (packages) bên ngoài mà dự án DBT sử dụng.
</code>
</pre>

## Đóng góp

Đóng góp cho dự án này rất được hoan nghênh. Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp.

## Hình ảnh
![image](https://github.com/user-attachments/assets/ed466765-cfa8-4912-aafc-c524b6abd20c)
![image](https://github.com/user-attachments/assets/11144f95-4a38-49b1-8dc2-c7c0142fe965)
![image](https://github.com/user-attachments/assets/56bf6af9-2c4e-4729-aaea-526826698144)




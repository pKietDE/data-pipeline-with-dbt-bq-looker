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

Tải file IP2Loc : ![link](https://lite.ip2location.com/database/db11-ip-country-region-city-latitude-longitude-zipcode-timezone)

## Cài đặt

1. Clone repository:
2. Di chuyển vào thư mục dự án:
3. Cài đặt các thư viện cần thiết:

## Sử dụng

Để chạy script, sử dụng lệnh sau:
+ python3 crawl_image_glamira.py # Script này sẽ crawl dữ liệu từ trang Glamira và lưu vào MongoDB.
+ upload_gcs.py # Script này sẽ export dữ liệu từ MongoDB và upload lên GCS.

## Cấu hình
1. Cấu hình Google Cloud:
- Đảm bảo bạn đã cài đặt và cấu hình Google Cloud SDK
- Thiết lập biến môi trường GOOGLE_APPLICATION_CREDENTIALS

## Luồng dữ liệu
1. Crawl dữ liệu từ Glamira -> MongoDB
2. Export từ MongoDB -> Google Cloud Storage
3. Xử lý dữ liệu bằng DBT trên BigQuery
4. Hiển thị kết quả trên Looker


## Cấu trúc dự án
project/
│
├── crawl_image_glamira.py   # Script chính để crawl dữ liệu
├── upload_gcs.py            # Script để upload các thư mục đã export từ MongoDB
├── requirements.txt         # Danh sách các thư viện cần thiết
├── README.md                # File này
│
├── config/
│   └── config.yaml          # File cấu hình cho dự án
│
├── data/
│   ├── raw/                 # Dữ liệu thô sau khi crawl
│   └── processed/           # Dữ liệu đã qua xử lý
│
├── dbt/
│   ├── models/              # Các model DBT
│   ├── macros/              # Macros DBT
│   └── dbt_project.yml      # File cấu hình DBT
│
└── docs/
└── images/              # Hình ảnh cho documentation

## Đóng góp

Đóng góp cho dự án này rất được hoan nghênh. Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp.

## Hình ảnh
![image](https://github.com/user-attachments/assets/ed466765-cfa8-4912-aafc-c524b6abd20c)


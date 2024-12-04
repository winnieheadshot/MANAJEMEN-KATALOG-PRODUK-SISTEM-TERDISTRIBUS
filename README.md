# MANAJEMEN KATALOG PRODUK SISTEM TERDISTRIBUSI

## Deskripsi

Sistem manajemen katalog produk berbasis REST API yang memungkinkan akses dari berbagai perangkat dengan autentikasi API key.

## Teknologi yang Digunakan

* Python 3.10
* Flask 2.0.1
* MySQL
* Flask-CORS

## Langkah-langkah Implementasi

### 0. Persiapan Lingkungan

```
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 1. Konfigurasi Database

```
-- Buat database
CREATE DATABASE product_catalog;
USE product_catalog;

-- Buat tabel products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT
);

-- Buat tabel api_keys
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_value VARCHAR(64) NOT NULL UNIQUE,
    client_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Konfigurasi Environment

```
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=product_catalog
```

### 3. Menjalankan Server

```
python app.py
```

### 4. Mendapatkan API Key

Gunakan Postman atau curl untuk mendapatkan API key:

```
curl -X POST http://localhost:5000/api/keys \
-H "Content-Type: application/json" \
-d "{\"client_name\":\"client1\"}"
```

### 5. Mengakses API dari Perangkat Lain

#### a. Install Dependencies di Perangkat Client

```
pip install requests
```

#### b. Gunakan Script Client

```
from client_api import ProductAPI

# Ganti dengan IP server dan API key yang diperoleh
SERVER_IP = '192.168.xxx.xxx'
API_KEY = 'your_api_key_here'

client = ProductAPI(SERVER_IP, API_KEY)

# Test koneksi
if client.test_connection():
    # Get all products
    products = client.get_products()
    print(products)
```

## Endpoint API yang Tersedia

### 1. Manajemen API Key

* `POST /api/keys` - Membuat API key baru

### 2. Manajemen Produk

* `GET /api/products` - Mendapatkan semua produk
* `GET /api/products/<id>` - Mendapatkan produk spesifik
* `POST /api/products` - Menambah produk baru
* `PUT /api/products/<id>` - Memperbarui produk
* `DELETE /api/products/<id>` - Menghapus produk

## Format Request dan Response

### Contoh Request POST Product

```
{
    "name": "Produk Test",
    "category": "Elektronik",
    "price": 99.99,
    "description": "Deskripsi produk"
}
```

### Headers yang Diperlukan

```
Content-Type: application/json
X-API-Key: your_api_key_here
```

## Penanganan Error

* 401: API key tidak valid/tidak ada
* 404: Resource tidak ditemukan
* 500: Server error

## Keamanan

* Menggunakan API key untuk autentikasi
* CORS enabled untuk akses cross-origin
* Rate limiting (opsional)

## Pengujian

```
# Jalankan unit tests
python -m pytest tests/
```

## Troubleshooting

1. Pastikan server MySQL berjalan
2. Periksa konfigurasi firewall untuk port 5000
3. Validasi API key pada header request
4. Periksa log server untuk error detail

## Kontribusi

Silakan buat pull request untuk kontribusi.

## Lisensi

MIT License

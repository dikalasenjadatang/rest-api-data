
# End-to-End-Testing
## Deskripsi

File ini menyediakan endpoint untuk  mengklasifikasikan artikel berita berdasarkan sentimen dan menganalisis persentase portal berita. Menggunakan Flask untuk melayani endpoint yang mengembalikan data dalam format JSON, dan Pandas untuk manipulasi dan analisis data.

## Struktur Direktori

    project-directory/
    │
    ├── scraping/
    │   └── berita/
    │       └── get_news.py
    │
    ├── utils/
    │   └── data/
    │       ├── utils_pie.py
    │       └── utils_groupsentimen.py
    │
    ├── endpoints/
    │   └── data/
    │       ├── pie_endpoint.py
    │       └── groupsentimen_endpoint.py
    │
    ├── app.py
    ├── requirements.txt
    └── README.md



`scraping/berita/get_news.py`  
Mengambil data berita. File ini berisi logika untuk mendapatkan data dari sumber berita, baik dari API, file, atau database.

`utils/data/data_utils.py`  
Berisi fungsi untuk memproses data berita, seperti menghitung jumlah berita per portal atau menghasilkan data untuk pie chart.

`utils/data/utils_pie.py`  
Menghasilkan data khusus untuk visualisasi pie chart berdasarkan informasi dari `get_news_data`.

`endpoints/data/data_endpoint.py`  
Mendefinisikan blueprint Flask dan endpoint `/api/news_data` untuk menyediakan data berita dalam format JSON.

`endpoints/data/pie_endpoint.py`  
Mendefinisikan blueprint Flask dan endpoint `/api/portal_percentage` untuk menyediakan data persentase portal dalam format JSON.

`app.py`  
File utama yang menjalankan aplikasi Flask, mendaftarkan blueprint, dan mengatur rute aplikasi.

`requirements.txt`  
Daftar dependensi Python yang dibutuhkan untuk menjalankan proyek, seperti Flask dan Pandas.


## Instalasi

1. **Clone Repositori**

   ```bash
   git clone <URL_REPOSITORI>
   cd end-to-end-testing


2. **Buat dan Aktifkan Virtual Environment**
    ```bash
    python -m venv env
    source env/bin/activate  # Untuk Windows: env\Scripts\activate

3. **Install Dependensi

Pastikan Anda memiliki requirements.txt yang mencantumkan dependensi proyek Anda, seperti Flask. Install dependensi dengan:
    ```bash
    pip install -r requirements.txt


## Menjalankan Aplikasi
Jalankan aplikasi Flask dengan perintah berikut:
    ```bash
    python app.py
    Aplikasi akan berjalan pada http://127.0.0.1:5000/ secara default.

## Mengakses Endpoint
Akses endpoint pie chart melalui browser atau alat seperti curl atau Postman di:
    ```bash
    [http://127.0.0.1:5000/api/news_classification](http://127.0.0.1:5000/api/news_classification)
    [http://127.0.0.1:5000/api/portal_percentage](http://127.0.0.1:5000/api/portal_persen)

## Ouput Data
Berikut adalah hasil endpoint:
1. Mendapatkan Klasifikasi Sentimen: 
   ```bash

       {
        "positif": [
            "Korupsi di Pemerintah",
            "Korupsi di BUMN",
            "Korupsi di Sektor Pendidikan"
        ],
        "negatif": [
            "Ekonomi Stabil",
            "Olahraga dan Kesehatan"
        ]
    }

2. Mendapatkan Persentase Portal
   ```bash
    {
        "labels": [
            "CNBC",
            "CNN",
            "Liputan6"
        ],
        "values": [
            20,
            40,
            40
        ]
    }



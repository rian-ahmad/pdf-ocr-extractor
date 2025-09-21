# PDF Content Extractor: OCR & Structured Data
Proyek ini adalah alat Python yang kuat untuk mengekstrak konten terstruktur dari dokumen PDF. Dengan menggunakan teknologi Optical Character Recognition (OCR) dan pemrosesan dokumen cerdas dari PaddleOCR, skrip ini mampu mengekstrak tidak hanya teks, tetapi juga tabel, gambar, dan formula dari file PDF, lalu menyimpannya dalam format JSON yang terstruktur.
Alat ini ideal untuk aplikasi yang memerlukan analisis data dari dokumen yang sulit diproses, seperti laporan keuangan, jurnal ilmiah, atau dokumen arsip.

## Fitur Utama
- Ekstraksi Teks: Mengambil teks dari dokumen, termasuk paragraf, judul, dan caption.
- Deteksi Tabel: Mengidentifikasi dan mengekstrak tabel, mengonversinya menjadi data terstruktur (JSON).
- Pengenalan Gambar dan Formula: Mendeteksi dan menyimpan gambar serta formula LaTeX.
- Output Terstruktur: Hasil ekstraksi disimpan dalam format JSON dengan metadata per halaman, sangat ideal untuk aplikasi RAG (Retrieval-Augmented Generation) dan analisis data.
- Otomatisasi: Memproses semua file PDF secara otomatis dari direktori sumber.

<hr>

## Teknologi yang Digunakan
- [PaddleOCR](https://www.paddleocr.ai/latest/en/index.html): Mesin OCR yang kuat dan efisien untuk mendeteksi teks dan struktur dokumen.
- [pdfplumber](https://github.com/jsvine/pdfplumber): Pustaka Python untuk mengakses metadata dari file PDF.
- [Pandas](https://pandas.pydata.org/): Digunakan untuk memproses data tabel yang diekstrak.
- [tqdm](https://tqdm.github.io/): Menambahkan progress bar yang informatif untuk memantau proses.

<hr>

## Instalasi
Pastikan Anda memiliki Python 3.8 atau yang lebih baru. Instal dependensi yang diperlukan dengan perintah berikut:
``` bash
pip install -r requirements.txt
```

## Cara Menggunakan
1. Buat folder bernama source di direktori proyek Anda.
2. Tempatkan semua file PDF yang ingin Anda proses di dalam folder source.
3. Buka file config.py. Anda dapat menyesuaikan direktori sumber dan keluaran, serta parameter OCR sesuai kebutuhan.
4. Jalankan skrip utama dari terminal:
``` bash
python your_main_script_name.py
```

## Hasil
- Setelah proses selesai, skrip akan membuat folder baru di dalam direktori output untuk setiap file PDF.
- File JSON yang berisi konten terstruktur dan gambar yang diekstrak akan tersimpan di sana.

## Contoh Output JSON
Berikut adalah contoh struktur data JSON yang dihasilkan. Perhatikan bagaimana setiap blok konten memiliki metadata `page_number` untuk konteks halaman, yang penting untuk RAG.
``` JSON
[
  {
    "label": "metadata_file",
    "data": {
      "nama_file": "contoh_laporan.pdf",
      "total_halaman": 5,
      "ukuran_kb": 256.78,
      "ukuran_mb": 0.25,
      "created_at": 1678886400,
      "modified_at": 1678886400
    }
  },
  {
    "page_idx": 0,
    "content": [
      {
        "label": "doc_title",
        "text": "Ringkasan Eksekutif",
        "metadata": {
          "page_number": 1
        }
      },
      {
        "label": "text",
        "text": "Laporan ini merinci kinerja perusahaan...",
        "metadata": {
          "page_number": 1
        }
      },
      {
        "label": "table",
        "data": [
          {
            "Tahun": "2022",
            "Pendapatan": "100M",
            "Laba": "20M"
          }
        ],
        "metadata": {
          "page_number": 1
        }
      }
    ]
  }
]
```

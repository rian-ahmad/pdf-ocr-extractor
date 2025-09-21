import os

# --- Konfigurasi Lokasi File ---
# Gunakan os.path.join untuk kompatibilitas lintas OS
SOURCE_DIR = "source" # Sesuaikan
OUTPUT_DIR = "output" # Sesuaikan

# --- Konfigurasi OCR ---
OCR_USE_DOC_ORIENTATION_CLASSIFY = False
OCR_USE_DOC_UNWARPING = False
OCR_USE_TEXTLINE_ORIENTATION = False
OCR_USE_CHART_RECOGNITION = True
OCR_USE_FORMULA_RECOGNITION = True
OCR_USE_TABLE_RECOGNITION = True
OCR_USE_REGION_DETECTION = True
OCR_LANG = 'id'
OCR_TEXT_DET_UNCLIP_RATIO = 1.6

# --- Pengaturan Logging ---
LOGGING_LEVELS = {
    "paddleocr": "ERROR",
    "pdfminer": "ERROR",
    "pdfplumber": "ERROR"
}

# --- Ekstensi File yang Didukung ---
SUPPORTED_EXTENSIONS = ['.pdf']
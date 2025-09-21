import logging
import warnings
import os
import re
import json
import pandas as pd
import pdfplumber
from tqdm import tqdm
from io import StringIO
from paddleocr import PPStructureV3

import config

# --- Konfigurasi dan Pengaturan Awal ---

for lib, level in config.LOGGING_LEVELS.items():
    logging.getLogger(lib).setLevel(level)

warnings.filterwarnings("ignore", category=UserWarning, module="paddleocr")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("extract_text.log")
    ]
)

ocr = PPStructureV3(
    use_doc_orientation_classify=config.OCR_USE_DOC_ORIENTATION_CLASSIFY,
    use_doc_unwarping=config.OCR_USE_DOC_UNWARPING,
    use_textline_orientation=config.OCR_USE_TEXTLINE_ORIENTATION,
    use_chart_recognition=config.OCR_USE_CHART_RECOGNITION,
    use_formula_recognition=config.OCR_USE_FORMULA_RECOGNITION,
    use_table_recognition=config.OCR_USE_TABLE_RECOGNITION,
    use_region_detection=config.OCR_USE_REGION_DETECTION,
    lang=config.OCR_LANG,
    text_det_unclip_ratio=config.OCR_TEXT_DET_UNCLIP_RATIO,
)

# --- FUNGSI-FUNGSI BANTUAN ---

def clean_latex_formula(raw_formula: str) -> str:
    """Membersihkan string formula LaTeX dari spasi yang tidak relevan."""
    return re.sub(r'\s+', ' ', raw_formula).strip()

def process_table(text: str) -> dict:
    """Memproses HTML tabel menjadi format dictionary."""
    try:
        df = pd.read_html(StringIO(text))[0]
        if not df.empty:
            header = df.iloc[0].tolist()
            df = df[1:].copy()
            df.columns = header
            table_data = df.to_dict('records')
            return {'label': 'table', 'data': table_data}
    except Exception as e:
        logging.error(f"Gagal memproses tabel: {e}")
        return {'label': 'table_error', 'text': text}
    return {'label': 'table', 'data': []}

def process_text_content(label: str, text: str) -> dict:
    """Memproses teks, judul, dan elemen lainnya."""
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    list_pattern = r'(?:\d+\.\s|\([a-z]\)\s|[\-•]\s)(.*?)(?=(?:\d+\.\s|\([a-z]\)\s|[\-•]\s|$))'
    matches = re.findall(list_pattern, cleaned_text, re.DOTALL)

    if matches:
        return {'label': 'list', 'text': [m.strip() for m in matches]}
    else:
        return {'label': label, 'text': cleaned_text}

def save_image(res, output_dir: str):
    """Menyimpan gambar dari hasil ekstraksi."""
    try:
        img_path = res.image.get('path')
        if not img_path:
            return
        
        full_img_path = os.path.join(output_dir, img_path)
        img_dir = os.path.dirname(full_img_path)
        os.makedirs(img_dir, exist_ok=True)
        res.image['img'].save(full_img_path)
    except Exception as e:
        logging.error(f"Gagal menyimpan gambar: {e}")

# --- FUNGSI UTAMA ---

def process_single_pdf(pdf_path: str):
    """
    Mengambil konten dari satu file PDF dan menyimpannya ke format JSON.
    """
    if not os.path.exists(pdf_path):
        logging.error(f"File tidak ditemukan: {pdf_path}")
        return

    name, _ = os.path.splitext(os.path.basename(pdf_path))
    output_dir = os.path.join(config.OUTPUT_DIR, name)
    os.makedirs(output_dir, exist_ok=True)
    
    ambil_label = ['text', 'paragraph_title', 'doc_title', 'header', 'figure_title', 'caption']
    docs = []

    try:
        outputs = ocr.predict_iter(pdf_path)
        
        # Ambil metadata keseluruhan file
        with pdfplumber.open(pdf_path) as pdf:
            stat_info = os.stat(pdf_path)
            metadata_file = {
                "nama_file": name,
                "total_halaman": len(pdf.pages),
                "ukuran_kb": round(stat_info.st_size / 1024, 2),
                "ukuran_mb": round(stat_info.st_size / (1024 * 1024), 2),
                "created_at": stat_info.st_ctime,
                "modified_at": stat_info.st_mtime
            }
        
        # Tambahkan metadata global di awal
        docs.append({'label': 'metadata_file', 'data': metadata_file})
        
        # Memproses setiap halaman
        for output in tqdm(outputs, desc="Memproses halaman"):
            page_index = output.get('page_index', -1)
            content = []
            
            metadata_page = {
                "page_number": page_index + 1
            }
            
            result = output.get('parsing_res_list', [])

            for res in result:
                label = res.label
                text = res.content.strip()

                if label in ambil_label:
                    content_dict = process_text_content(label, text)
                    content_dict['metadata'] = metadata_page
                    content.append(content_dict)
                elif label == 'table':
                    content_dict = process_table(text)
                    content_dict['metadata'] = metadata_page
                    content.append(content_dict)
                elif label == 'image':
                    save_image(res, output_dir)
                    img_path = res.image.get('path')
                    if img_path:
                        content.append({'label': 'image', 'img_path': img_path, 'metadata': metadata_page})
                elif label == 'formula':
                    cleaned_formula = clean_latex_formula(text)
                    content.append({'label': 'formula', 'formula_latex': cleaned_formula, 'metadata': metadata_page})
            
            # Ini akan mengumpulkan semua konten dari satu halaman
            if content:
                docs.append({
                    'page_idx': page_index,
                    'content': content
                })

    except Exception as e:
        logging.error(f"Gagal memproses dokumen {pdf_path}: {e}")
        return

    # Simpan file JSON
    json_path = os.path.join(output_dir, f"{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Selesai, file JSON disimpan di {json_path}")

def main():
    """Fungsi utama untuk memproses semua file PDF di direktori sumber."""
    logging.info("Memulai proses ekstraksi OCR untuk semua file PDF.")
    
    if not os.path.exists(config.SOURCE_DIR):
        logging.error(f"Direktori sumber tidak ditemukan: {config.SOURCE_DIR}")
        return
        
    for filename in os.listdir(config.SOURCE_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(config.SOURCE_DIR, filename)
            logging.info(f"Memproses file: {pdf_path}")
            process_single_pdf(pdf_path)
    
    logging.info("Semua file PDF selesai diproses.")

# --- Eksekusi ---
if __name__ == "__main__":
    main()
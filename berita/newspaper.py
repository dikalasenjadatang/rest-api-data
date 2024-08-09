import requests
from bs4 import BeautifulSoup
import os
import pytesseract
from PIL import Image
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/scrape', methods=['POST'])
def scrape_newspaper():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400

    output_folder = "downloaded_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all('img')

        downloaded_images = []
        extracted_texts = []

        for i, img in enumerate(images):
            src = img.get('src')
            if src:
                try:
                    # Tangani URL gambar relatif atau absolut
                    if not src.startswith(('http:', 'https:')):
                        src = requests.compat.urljoin(url, src)

                    img_data = requests.get(src).content
                    image_path = os.path.join(output_folder, f"image_{i}.jpg")
                    with open(image_path, 'wb') as handler:
                        handler.write(img_data)
                    logging.info(f"Downloaded image_{i}.jpg")

                    # Verifikasi bahwa file yang diunduh adalah gambar yang valid
                    try:
                        with Image.open(image_path) as img:
                            img.verify()
                        logging.info(f"Downloaded and verified image_{i}.jpg")
                    except Exception as e:
                        logging.error(f"Invalid image file: image_{i}.jpg. Error: {e}")
                        os.remove(image_path)  # Hapus file yang tidak valid
                        continue

                    # Cek apakah Tesseract tersedia
                    if not pytesseract.is_tesseract_available():
                        logging.warning("Tesseract is not available. Skipping OCR.")
                        continue

                    # Lakukan OCR pada gambar yang diunduh
                    try:
                        text = pytesseract.image_to_string(Image.open(image_path), lang='ind')
                        
                        # Simpan hasil OCR ke file teks
                        text_file_path = os.path.join(output_folder, f"text_{i}.txt")
                        with open(text_file_path, 'w', encoding='utf-8') as text_file:
                            text_file.write(text)
                        
                        logging.info(f"Extracted text from image_{i}.jpg and saved to text_{i}.txt")
                        downloaded_images.append(f"image_{i}.jpg")
                        extracted_texts.append(f"text_{i}.txt")
                    except Exception as e:
                        logging.error(f"Failed to perform OCR on image_{i}.jpg. Error: {e}")

                except requests.exceptions.RequestException as e:
                    logging.error(f"Failed to download image from {src}. Error: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error processing {src}. Error: {e}")

        result = {
            "message": "Scraping completed",
            "url": url,
            "images_downloaded": downloaded_images,
            "texts_extracted": extracted_texts,
            "output_folder": output_folder
        }
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"An error occurred: {str(e)}")
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
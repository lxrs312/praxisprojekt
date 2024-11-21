from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from pytesseract import Output
import json
import os
import io


class TesseractHandler:
    def __init__(self, tesseract_cmd: str = None):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.__data = None

    def analyzeDocument(self, path_to_pdf: str):
        """
        analysiert ein dokument mit pytesseract.
        akzeptiert pdf- oder bilddaten als bytes.
        """
        # versuche pdf zu konvertieren, ansonsten bilde öffnen
        with open(path_to_pdf, "rb") as f:
            pdf_bytes = f.read()

        images = convert_from_bytes(pdf_bytes)
        self.__data = []
        for page_image in images:
            page_data = pytesseract.image_to_data(page_image, output_type=Output.DICT, lang="deu")
            self.__data.append(page_data)

    def saveData(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        """speichert rohdaten und extrahierte wörter"""
        # speichere rohdaten
        
        with open(os.path.join('tesseract', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

        # extrahiere relevante wörter
        word_data = []
        for page_data in self.__data:
            for i, block_type in enumerate(page_data.get('block_num', [])):
                if page_data['text'][i].strip():
                    word_data.append(page_data['text'][i])

        # aktualisiere processedData.json
        processed_data_path = os.path.join('tesseract', 'processedData.json')
        if os.path.exists(processed_data_path):
            with open(processed_data_path, "r", encoding="utf8") as f:
                processed_data = json.load(f)
        else:
            processed_data = {}

        if str(document) not in processed_data:
            processed_data[str(document)] = {}

        processed_data[str(document)][str(exemplar)] = {
            "wordData": word_data,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }

        with open(processed_data_path, "w", encoding="utf8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    client = TesseractHandler()
    client.analyzeDocument('pdfs/test.pdf')
    client.saveData(1, 1, 30, 30, 30)
    
    
    
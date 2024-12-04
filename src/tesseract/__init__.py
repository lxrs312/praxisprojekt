from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from pytesseract import Output
import json
import os
import io

from misc.normalizer import OCRTextNormalizer
from misc.filehandler import FileHandler

class TesseractHandler(FileHandler):
    def __init__(self, data_path: str, logger):
        super().__init__(logger, data_path)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.__normalizer = OCRTextNormalizer()

    def analyze_document(self, path_to_pdf: str):
        """
        analysiert ein dokument mit pytesseract.
        akzeptiert pdf- oder bilddaten als bytes.
        """
        # versuche pdf zu konvertieren, ansonsten bilde öffnen
        with open(path_to_pdf, "rb") as f:
            pdf_bytes = f.read()

        images = convert_from_bytes(pdf_bytes)
        word_list = []
        for page_image in images:
            page_data = pytesseract.image_to_data(page_image, output_type=Output.DICT, lang="deu")
            word_list.append(page_data)
        
        self._data = word_list

    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        """speichert rohdaten und extrahierte wörter"""
        # speichere rohdaten

        wordData = []
        for page_data in self._data:
            for i, block_type in enumerate(page_data.get('block_num', [])):
                if page_data['text'][i].strip():
                    normalized_words = self.__normalizer.normalize(page_data['text'][i])
                    
                    for word in normalized_words:
                        if word:
                            wordData.append({'word': word, 'confidence': page_data['conf'][i]})

        self.handle_data(
            processed_word_data=wordData,
            document=document,
            exemplar=exemplar,
            processingTime=processingTime,
            pingBefore=pingBefore,
            pingAfter=pingAfter
        )
    
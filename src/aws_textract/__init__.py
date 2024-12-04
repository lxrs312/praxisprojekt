import os, json, sys

import boto3

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer
from misc.filehandler import FileHandler

REGION = "eu-central-1"

class TextractHandler(FileHandler):
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, data_path: str, logger):
        super().__init__(logger, data_path)
        self.__client = boto3.client('textract', region_name=REGION, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.__normalizer = OCRTextNormalizer()

    def analyze_document(self, path_to_pdf: str):
        """analyzes a document using aws textract"""
        with open(path_to_pdf, "rb") as document:
            response = self.__client.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['FORMS']
            )
        
        # speichere rohdaten
        self._data = response
        
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):

        # extract only relevant words for words.json
        wordData = []
        for block in self.data.get('Blocks'):
            if block.get('BlockType') == "WORD":
                normalized_words = self.__normalizer.normalize(block.get('Text'))
                
                for word in normalized_words:
                    if word:
                        wordData.append({'word': word, 'confidence': block.get('Confidence')})

        self.handle_data(
            processed_word_data=wordData,
            document=document,
            exemplar=exemplar,
            processingTime=processingTime,
            pingBefore=pingBefore,
            pingAfter=pingAfter
        )

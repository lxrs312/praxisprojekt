import os, json, sys

import boto3

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer

REGION = "eu-central-1"

class TextractHandler:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str):
        self.__client = boto3.client('textract', region_name=REGION, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.__data = None
        self.__normalizer = OCRTextNormalizer()

    def analyze_document(self, path_to_pdf: str):
        """analyzes a document using aws textract"""
        with open(path_to_pdf, "rb") as document:
            response = self.__client.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['FORMS']
            )
        
        # speichere rohdaten
        self.__data = response
        
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):

        # firstly save raw data into raw_data directory
        with open(os.path.join('data', 'aws_textract', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

        # extract only relevant words for words.json
        wordData = []
        for block in self.__data.get('Blocks'):
            if block.get('BlockType') == "WORD":
                normalized_words = self.__normalizer.normalize(block.get('Text'))
                
                for word in normalized_words:
                    if word:
                        wordData.append({'word': word, 'confidence': block.get('Confidence')})

        # open processedData.json
        processed_data_path = os.path.join('data', 'aws_textract','processedData.json')
        if os.path.exists(processed_data_path):
            with open(processed_data_path, "r", encoding="utf8") as f:
                processedData = json.load(f)
        else:
            processedData = {}
        
        if not processedData.get(str(document)):
            processedData[str(document)] = {}
        
        processedData[str(document)][str(exemplar)] = {
            "wordData": wordData,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }
        
        # save processedData.json
        with open(processed_data_path, "w", encoding="utf8") as f:
             json.dump(processedData, f, ensure_ascii=False, indent=4)

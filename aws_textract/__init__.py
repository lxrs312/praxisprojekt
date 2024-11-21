import boto3
import json
import os

REGION = "eu-central-1"

class TextractHandler:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str):
        self.__client = boto3.client('textract', region_name=REGION, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.__data = None

    def analyzeDocument(self, path_to_pdf: str):
        """analyzes a document using aws textract"""
        with open(path_to_pdf, "rb") as document:
            response = self.__client.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['FORMS']
            )
        
        # speichere rohdaten
        self.__data = response
        
    def saveData(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):

        # firstly save raw data into raw_data directory
        with open(os.path.join('aws_textract', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

        # extract only relevant words for words.json
        wordData = []
        for block in self.__data.get('Blocks'):
            if block.get('BlockType') == "WORD":
                wordData.append(block.get('Text'))

        # open processedData.json
        with open(os.path.join('aws_textract','processedData.json'), "r", encoding="utf8") as f:
            processedData = json.load(f)
        
        processedData[str(document)][str(exemplar)] = {
            "wordData": wordData,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }
        
        # save processedData.json
        with open(os.path.join('aws_textract','processedData.json'), "w", encoding="utf8") as f:
             json.dump(processedData, f, ensure_ascii=False, indent=4)

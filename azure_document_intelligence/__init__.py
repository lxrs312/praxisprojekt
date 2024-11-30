import os, json, sys

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer

class DocumentIntelligenceHandler:
    def __init__(self, endpoint, key):
        #self.__client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        self.__data = None
        self.__normalizer = OCRTextNormalizer()

    def analyze_document(self, pathToPdf: str):
        """starts analyzing the document

        Args:
            client (DocumentIntelligenceClient): actual client
            pathToPdf (str):
        Returns:
            data (dict): the data
        """
        with open(pathToPdf, "rb") as f:
            poller = self.__client.begin_analyze_document(
                "prebuilt-layout",
                analyze_request=f,
                content_type="application/octet-stream",
            )
            
        result: AnalyzeResult = poller.result()
    
        self.__data = result.pages[0].as_dict()
    
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        
        # firstly save raw data into raw_data directory
        with open(os.path.join('data', 'azure_document_intelligence', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

        # extract only relevant words for words.json
        wordData = []
        for word_obj in self.__data.get('words'):
            normalized_words = self.__normalizer.normalize(word_obj.get('content'))
                
            for word in normalized_words:
                if word:
                    wordData.append({'word': word, 'confidence': word_obj.get('confidence')})

        # open processedData.json
        processed_data_path = os.path.join('data', 'azure_document_intelligence','processedData.json')
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


import os, json, sys

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer
from misc.filehandler import FileHandler

class DocumentIntelligenceHandler(FileHandler):
    def __init__(self, endpoint, key, data_path: str, logger):
        super().__init__(logger, data_path)
        self.__client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
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
    
        self._data = result.pages[0].as_dict()
    
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        
        # extract only relevant words for words.json
        wordData = []
        for word_obj in self.data.get('words'):
            normalized_words = self.__normalizer.normalize(word_obj.get('content'))
                
            for word in normalized_words:
                if word:
                    wordData.append({'word': word, 'confidence': word_obj.get('confidence')})

        self.handle_data(
            processed_word_data=wordData,
            document=document,
            exemplar=exemplar,
            processingTime=processingTime,
            pingBefore=pingBefore,
            pingAfter=pingAfter
        )
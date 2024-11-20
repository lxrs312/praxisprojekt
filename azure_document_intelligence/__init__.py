import os
import json

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

class DocumentIntelligenceHandler:
    def __init__(self, endpoint, key):
        self.__client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        self.__data = None

    def analyzeDocument(self, pathToPdf: str):
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
    
    def saveData(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        
        # firstly save raw data into raw_data directory
        with open(os.path.join('azure_document_intelligence', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

        # extract only relevant words for words.json
        wordData = []
        for word in self.__data.get('words'):
            wordData.append(word.get('content'))

        # open processedData.json
        with open(os.path.join('azure_document_intelligence','processedData.json'), "r", encoding="utf8") as f:
            processedData = json.load(f)
        
        processedData[str(document)][str(exemplar)] = {
            "wordData": wordData,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }
        
        # save processedData.json
        with open(os.path.join('azure_document_intelligence','processedData.json'), "w", encoding="utf8") as f:
             json.dump(processedData, f, ensure_ascii=False, indent=4)
        

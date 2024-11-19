from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

class DocumentIntelligence():
    def __init__(self, endpoint, key):
        self.__client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

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
                features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
                content_type="application/octet-stream",
            )
            
        result: AnalyzeResult = poller.result()
    
        data = result.pages[0].as_dict()
        
        return data

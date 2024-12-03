import os, json, sys, time

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer
from misc.filehandler import FileHandler
from timehandler import TimeHandler
from dotenv import load_dotenv

load_dotenv()

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
        
if __name__ == '__main__':
    data_path = os.path.join('data', 'azure_document_intelligence')
    client = DocumentIntelligenceHandler(os.environ.get('AZURE_ENDPOINT'), os.environ.get('AZURE_KEY'), data_path, None)
    time_handler = TimeHandler()

    for document in range(1, 11):
        print(f"Processing document {document}")
        for exemplar in range(1, 11):
            print(f"Processing exemplar {document}-{exemplar}")
            exemplar_name = f"0{exemplar}" if exemplar < 10 else exemplar
            pdf_path = os.path.join('pdfs', 'scans', str(document), f'{exemplar_name}.pdf')
            time_handler.startTimer()
            client.analyze_document(pdf_path)
            processingTime = time_handler.stopTimer()
            client.save_data(document, exemplar, processingTime, 0, 0)
            time.sleep(5)
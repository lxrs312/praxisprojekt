
import os, json, sys

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.protobuf.json_format import MessageToDict

LOCATION = "eu"
MIME_TYPE = "application/pdf"
PROCESSOR_VERSION = "rc"

sys.path.append('../praxisprojekt')

from src.misc.normalizer import OCRTextNormalizer
from src.misc.filehandler import FileHandler

class GoogleCloudDocumentAI(FileHandler):
    def __init__(self, auth_file_path: str, project_id: str, processor_id: str, data_path: str, logger):
        super().__init__(logger, data_path)
        self.__client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{LOCATION}-documentai.googleapis.com",
                credentials_file=auth_file_path
            )
        )
        
        self.__name = self.__client.processor_version_path(
            project_id, LOCATION, processor_id, PROCESSOR_VERSION
        )
        
        self.__process_options = documentai.ProcessOptions(
            ocr_config=documentai.OcrConfig(
                enable_native_pdf_parsing=True,
            )
        )
        
        self.__normalizer = OCRTextNormalizer()

    def analyze_document(self, path_to_pdf: str):
        """analyzes a document using document ai"""
        with open(path_to_pdf, "rb") as file:
            file_content = file.read()
            
        request = documentai.ProcessRequest(
            name=self.__name,
            raw_document=documentai.RawDocument(content=file_content, mime_type=MIME_TYPE),
            # Only supported for Document OCR processor
            process_options=self.__process_options,
        )
        
        result = self.__client.process_document(request=request)
        
        # speichere rohdaten
        self._data = result

    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):

        # dict conversion
        data_dict = MessageToDict(self._data.document._pb)
        
        # overwrite potential image key to avoid pushing too much data to github
        data_dict['pages'][0]['image'] = "saving-data.."

        self._data = data_dict

        wordData = []

        # extract only relevant words for words.json
        for page in self._data.get("pages", []):
            for token in page.get("tokens", []):
                layout = token.get("layout", {})
                confidence = layout.get("confidence", None)
                text_anchor = layout.get("textAnchor", {})
                text_segments = text_anchor.get("textSegments", [])
                
                # wörter mit start- und endindex finden
                for segment in text_segments:
                    start_index = int(segment.get("startIndex", 0))
                    end_index = int(segment.get("endIndex", 0))
                    
                    # wort extrahieren
                    word = data_dict.get("text", "")[start_index:end_index].strip()
                    
                    normalized_words = self.__normalizer.normalize(word)
                    
                    for normalized_word in normalized_words:
                        # hinzufügen, wenn confidence vorhanden
                        if normalized_word and confidence is not None:
                            wordData.append({'word': normalized_word, 'confidence': confidence})

        self.handle_data(
            processed_word_data=wordData,
            document=document,
            exemplar=exemplar,
            processingTime=processingTime,
            pingBefore=pingBefore,
            pingAfter=pingAfter
        )

import os, json, sys

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.protobuf.json_format import MessageToDict

LOCATION = "eu"
MIME_TYPE = "application/pdf"
PROCESSOR_VERSION = "rc"

sys.path.append('../praxisprojekt')

from misc.normalizer import OCRTextNormalizer

class GoogleCloudDocumentAI:
    def __init__(self, auth_file_path: str, project_id: str, processor_id: str):
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
        
        self.__data = None
        
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
        self.__data = result

        
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):

        # dict conversion
        data_dict = MessageToDict(self.__data.document._pb)
        
        # overwrite potential image key to avoid pushing too much data to github
        data_dict['pages'][0]['image'] = "saving-data.."

        # firstly save raw data into raw_data directory
        with open(os.path.join('google_cloud_document_ai', 'raw_data', str(document), f"{exemplar}.json"), "w", encoding="utf8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
        
        wordData = []

        # extract only relevant words for words.json
        for page in data_dict.get("pages", []):
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

        # open processedData.json
        with open(os.path.join('google_cloud_document_ai','processedData.json'), "r", encoding="utf8") as f:
            processedData = json.load(f)
        
        processedData[str(document)][str(exemplar)] = {
            "wordData": wordData,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }
        
        # save processedData.json
        with open(os.path.join('google_cloud_document_ai','processedData.json'), "w", encoding="utf8") as f:
             json.dump(processedData, f, ensure_ascii=False, indent=4)


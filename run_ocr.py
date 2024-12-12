import os, logging, asyncio, time

from dotenv import load_dotenv

from src.azure_document_intelligence import DocumentIntelligenceHandler
from src.aws_textract import TextractHandler
from src.google_cloud_document_ai import GoogleCloudDocumentAI
from src.misc.timehandler import TimeHandler
from src.tesseract import TesseractHandler
from src.misc.normalizer import OCRTextNormalizer
# from src.gpt4o import GPT4oHandler

load_dotenv()

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("simple_logger")

ocr_tools = ['aws_textract', 'azure_document_intelligence', 'google_cloud_document_ai', 'openai_gpt4o', 'tesseract']

def create_data_directory_structure():
    """
        creates the directory strucure for the data-directory
    """
    logger.info('creating data-directory-structure')
    if not os.path.exists('data'):
        os.mkdir('data')
    
    for tool in ocr_tools:
        logger.info(f'currently creating for {tool}')
        parent_path = os.path.join('data', tool)
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)
        
        raw_data_path = os.path.join(parent_path, 'raw_data')
        if not os.path.exists(raw_data_path):
            os.mkdir(raw_data_path)
        
        for i in range(1, 11):
            raw_data_document_path = os.path.join(raw_data_path, str(i))
            if not os.path.exists(raw_data_document_path):
                os.mkdir(raw_data_document_path)

# Beispielablauf Azure, aus irgendeinem Grund nicht in der main ausführbar -> runtime differences?!
def azure():
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
            time.sleep(2)

# Beispielablauf AWS
def aws():
    data_path = os.path.join('data', 'aws_textract')
    client = TextractHandler(os.environ.get('AWS_ACCESS_KEY'), os.environ.get('AWS_SECRET_ACCESS_KEY'), data_path, logger)
    time_handler = TimeHandler()

    for document in range(1, 11):
        print(f"Processing document {document}")
        for exemplar in range(1, 11):
            print(f"Processing exemplar {document}-{exemplar}")
            exemplar_name = f"0{exemplar}" if exemplar < 10 else exemplar
            time_handler.startTimer()
            client.analyze_document(os.path.join('pdfs', 'scans', str(document), f'{exemplar_name}.pdf'))
            processingTime = time_handler.stopTimer()
            client.save_data(document, exemplar, processingTime, 0, 0)
            time.sleep(5)
            
# Beispielablauf Document AI
def google():
    data_path = os.path.join('data', 'google_cloud_document_ai')
    client = GoogleCloudDocumentAI('googleauth.json', os.environ.get('PROJECT_ID'), os.environ.get('PROCESSOR_ID'), data_path, logger) 
    time_handler = TimeHandler()

    for document in range(1, 11):
        print(f"Processing document {document}")
        for exemplar in range(1, 11):
            print(f"Processing exemplar {document}-{exemplar}")
            exemplar_name = f"0{exemplar}" if exemplar < 10 else exemplar
            time_handler.startTimer()
            client.analyze_document(os.path.join('pdfs', 'scans', str(document), f'{exemplar_name}.pdf'))
            processingTime = time_handler.stopTimer()
            client.save_data(document, exemplar, processingTime, 0, 0)
            time.sleep(5)

def gpt4o():
    data_path = os.path.join('data', 'openai_gpt4o')
    client = GPT4oHandler(os.getenv('client_id'), os.getenv('client_secret'), os.getenv('token_url'), os.getenv('api_base'), os.getenv('chat'), data_path, logger)
    time_handler = TimeHandler()
    async def process_documents():
        for document in range(2, 3):
            print(f"Processing document {document}")
            for exemplar in range(6, 11):
                print(f"Processing exemplar {document}-{exemplar}")
                exemplar_name = f"0{exemplar}" if exemplar < 10 else exemplar
                time_handler.startTimer()
                await client.analyze_document(os.path.join('pdfs', 'scans', str(document), f'{exemplar_name}.pdf'))
                processingTime = time_handler.stopTimer()
                client.save_data(document, exemplar, processingTime, 0, 0)
                await asyncio.sleep(5)

    asyncio.run(process_documents())

def tesseract():
    data_path = os.path.join('data', 'tesseract')
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    client = TesseractHandler(tesseract_cmd, data_path, logger) 
    time_handler = TimeHandler()

    for document in range(1, 11):
        print(f"Processing document {document}")
        for exemplar in range(1, 11):
            print(f"Processing exemplar {document}-{exemplar}")
            exemplar_name = f"0{exemplar}" if exemplar < 10 else exemplar
            time_handler.startTimer()
            client.analyze_document(os.path.join('pdfs', 'scans', str(document), f'{exemplar_name}.pdf'))
            processingTime = time_handler.stopTimer()
            client.save_data(document, exemplar, processingTime, 0, 0)
            time.sleep(5)

# gpt4o()
# aws()
azure() 
# google()
# tesseract()
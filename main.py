import os, logging

# from azure_document_intelligence import DocumentIntelligenceHandler
# from aws_textract import TextractHandler
# from google_cloud_document_ai import GoogleCloudDocumentAI
# from timehandler import TimeHandler
# from misc.normalizer import OCRTextNormalizer

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


# Beispielablauf
def azure():
    client = DocumentIntelligenceHandler('https://endpoint/', 'key')
    time_handler = TimeHandler()

    pingBefore = time_handler.pingServer('endpoint')
    time_handler.startTimer()
    client.analyzeDocument(os.path.join('pdfs', 'test.pdf'))
    processingTime = time_handler.stopTimer()
    pingAfter = time_handler.pingServer('endpoint')

    client.saveData(1, 1, processingTime, pingBefore, pingAfter)


def aws():
    client = TextractHandler("key-1", "key-2")
    time_handler = TimeHandler()

    pingBefore = time_handler.pingServer('ec2.eu-central-1.amazonaws.com')
    time_handler.startTimer()
    client.analyzeDocument(os.path.join('pdfs', 'test.pdf'))
    processingTime = time_handler.stopTimer()
    pingAfter = time_handler.pingServer('ec2.eu-central-1.amazonaws.com')

    client.saveData(1, 1, processingTime, pingBefore, pingAfter)

def google():
    client = GoogleCloudDocumentAI('googleauth.json', project_id, processor_id) 
    time_handler = TimeHandler()
    
    pingBefore = time_handler.pingServer('eu-documentai.googleapis.com')
    time_handler.startTimer()
    client.analyze_document(os.path.join('pdfs', 'test.pdf'))
    processingTime = time_handler.stopTimer()
    pingAfter = time_handler.pingServer('eu-documentai.googleapis.com')

    client.save_data(1, 1, processingTime, pingBefore, pingAfter)

create_data_directory_structure()
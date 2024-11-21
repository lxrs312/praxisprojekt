import os

from azure_document_intelligence import DocumentIntelligenceHandler
from aws_textract import TextractHandler
from google_cloud_document_ai import GoogleCloudDocumentAI
from timehandler import TimeHandler

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


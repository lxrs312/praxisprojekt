import os

from azure_document_intelligence import DocumentIntelligenceHandler
from aws_textract import TextractHandler
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

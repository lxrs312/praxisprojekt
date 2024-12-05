import os, json

from src.misc.normalizer import OCRTextNormalizer
from src.misc.evaluator import Evaluator

ocr_tools = ['aws_textract', 'azure_document_intelligence', 'google_cloud_document_ai', 'openai_gpt4o', 'tesseract']

normalizer = OCRTextNormalizer()

with open(os.path.join('data', 'input_data.json'), "r", encoding="utf8") as f:
    input_data = json.load(f)
    
evaluatedData = {}

for tool in ocr_tools:
    print(f"Processing Tool {tool}")
    
    with open(os.path.join('data', tool, 'processedData.json'), "r", encoding="utf8") as f:
        processed_data = json.load(f)
        
    evaluatedData[tool] = {}
    
    for document in range(1, 11):
        print(f"Processing Document {document}")
        
        machine_list = input_data[str(document)]['maschinelle_woerter']
        
        normalized_machine_list = normalizer.normalize(machine_list)
        
        evaluator = Evaluator(normalized_machine_list)
        
        evaluatedData[tool][str(document)] = {}
        
        for exemplar in range(1, 11):
            print(f"Processing Document {document}-{exemplar}")
            
            recognized_words = processed_data[str(document)][str(exemplar)]['wordData']
            processing_time = processed_data[str(document)][str(exemplar)]['processingTime']
            
            handwritten_list = input_data[str(document)]['exemplare'][str(exemplar)]['handgeschriebene_woerter']
            evaluator.handwritten_list = normalizer.normalize(handwritten_list)
            
            result = evaluator.run(recognized_words, processing_time)
            
            evaluatedData[tool][str(document)][str(exemplar)] = result.as_dict()
            
            evaluatedData[tool][str(document)][str(exemplar)]['schriftfarbe'] = input_data[str(document)]['exemplare'][str(exemplar)]['schriftfarbe']

            evaluatedData[tool][str(document)][str(exemplar)]['autor'] = input_data[str(document)]['exemplare'][str(exemplar)]['autor']

with open(os.path.join('data', 'evaluatedData.json'), "w", encoding="utf8") as f:
    json.dump(evaluatedData, f, ensure_ascii=False, indent=4)
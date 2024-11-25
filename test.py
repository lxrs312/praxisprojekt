import json, os

from misc.classes.evaluator import Evaluator
from misc.classes.normalizer import OCRTextNormalizer

with open(os.path.join('input_data.json'), "r", encoding="utf8") as f:
    input_data = json.load(f)

with open(os.path.join('aws_textract', 'processedData.json'), "r", encoding="utf8") as f:
    aws_data = json.load(f)

aws_words = aws_data['1']['1']['wordData']

normalizer = OCRTextNormalizer()
normalized = normalizer.normalize(aws_words)

machine_list = normalizer.normalize(input_data['1']['maschinelle_woerter'])

handwritten_list = normalizer.normalize(input_data['1']['exemplare']['1']['handgeschriebene_woerter'])

evaluator = Evaluator(machine_list, handwritten_list)
result = evaluator.run(normalized)

print(result.as_dict())
import json, os, sys
import matplotlib.pyplot as plt

from pprint import pprint

from misc.evaluator import Evaluator
from misc.normalizer import OCRTextNormalizer

with open(os.path.join('input_data.json'), "r", encoding="utf8") as f:
    input_data = json.load(f)

with open(os.path.join('aws_textract', 'processedData.json'), "r", encoding="utf8") as f:
    aws_data = json.load(f)

aws_words = aws_data['1']['1']['wordData']

with open(os.path.join('azure_document_intelligence', 'processedData.json'), "r", encoding="utf8") as f:
    azure_data = json.load(f)

azure_words = azure_data['1']['1']['wordData']

with open(os.path.join('output.json'), "r", encoding="utf8") as f:
    output_data = json.load(f)

normalizer = OCRTextNormalizer()

machine_list = normalizer.normalize(input_data['1']['maschinelle_woerter'])

handwritten_list = normalizer.normalize(input_data['1']['exemplare']['1']['handgeschriebene_woerter'])

evaluator = Evaluator(machine_list, handwritten_list)
result = evaluator.run(aws_words)
result2 = evaluator.run(azure_words)

print(result.word_correct_machine)
print(result.letter_correct_machine)

pprint(result.as_dict())
pprint(result2.as_dict())

word_prob_machine = result.word_matches_machine/result.word_count_machine
word_prob_handwritten = result.word_matches_handwritten/result.word_count_handwritten

letter_prob_machine = result.letter_matches_machine/result.letter_count_machine
letter_prob_handwritten = result.letter_matches_handwritten/result.letter_count_handwritten

word_prob_machine_azure = result2.word_matches_machine/result2.word_count_machine
word_prob_handwritten_azure = result2.word_matches_handwritten/result2.word_count_handwritten

letter_prob_machine_azure = result2.letter_matches_machine/result2.letter_count_machine
letter_prob_handwritten_azure = result2.letter_matches_handwritten/result2.letter_count_handwritten

# labels und daten
labels = ['Maschine', 'Handgeschrieben']
word_probs_aws = [word_prob_machine, word_prob_handwritten]
letter_probs_aws = [letter_prob_machine, letter_prob_handwritten]
word_probs_azure = [word_prob_machine_azure, word_prob_handwritten_azure]
letter_probs_azure = [letter_prob_machine_azure, letter_prob_handwritten_azure]

# dark theme aktivieren
plt.style.use('dark_background')

# subplot setup
fig, ax = plt.subplots(2, 2, figsize=(12, 10), sharey=True)

# aws wort kategorien
ax[0, 0].bar(labels, word_probs_aws, color=['deepskyblue', 'gold'])
ax[0, 0].set_title('AWS - Wort')
ax[0, 0].set_ylabel('Wahrscheinlichkeit')
ax[0, 0].set_ylim(0, 1)

# azure wort kategorien
ax[0, 1].bar(labels, word_probs_azure, color=['deepskyblue', 'gold'])
ax[0, 1].set_title('Azure - Wort')

# aws buchstaben kategorien
ax[1, 0].bar(labels, letter_probs_aws, color=['deepskyblue', 'gold'])
ax[1, 0].set_title('AWS - Buchstaben')
ax[1, 0].set_ylabel('Wahrscheinlichkeit')
ax[1, 0].set_ylim(0, 1)

# azure buchstaben kategorien
ax[1, 1].bar(labels, letter_probs_azure, color=['deepskyblue', 'gold'])
ax[1, 1].set_title('Azure - Buchstaben')

# wahrscheinlichkeiten als text hinzufügen
for i, prob in enumerate(word_probs_aws):
    ax[0, 0].text(i, prob + 0.03, f'{prob:.2f}', ha='center', va='bottom', color='white')
for i, prob in enumerate(word_probs_azure):
    ax[0, 1].text(i, prob + 0.03, f'{prob:.2f}', ha='center', va='bottom', color='white')
for i, prob in enumerate(letter_probs_aws):
    ax[1, 0].text(i, prob + 0.03, f'{prob:.2f}', ha='center', va='bottom', color='white')
for i, prob in enumerate(letter_probs_azure):
    ax[1, 1].text(i, prob + 0.03, f'{prob:.2f}', ha='center', va='bottom', color='white')

# allgemeine layout-anpassung
fig.suptitle('Wahrscheinlichkeiten nach Kategorie (AWS vs. Azure)', fontsize=16)
plt.tight_layout()

# anzeigen
plt.show()
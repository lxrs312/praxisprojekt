import os
import json

def calc_average(input_list, size):
    return sum(input_list) / size

def summarize_metrics(data, data_keys_per_document, data_keys_overall, blacklist):
    summarized_data = {}
    blanko_data = {}

    autoren_data = {autor: {} for autor in ['lars', 'sarah', 'robin', 'tim', 'pascal']}
    schriftfarben_data = {farbe: {} for farbe in ['blau', 'schwarz']}
    
    for key, value in data.items():
        blanko_data[key] = {'documents': {}}
        key_dict = {}
        machine_confidence_list, handwritten_confidence_list = [], []
        processing_time = 0
        for document_nr, document_data in value.items():
            doc_dict = {}

            for exemplar_nr, metrics in document_data.items():
                schriftfarbe, autor = metrics['schriftfarbe'], metrics['autor']

                for metric_name, metric_value in metrics.items():
                    if metric_name in blacklist:
                        continue
                    
                    if metric_name in data_keys_per_document:
                        doc_dict.setdefault(metric_name, []).append(metric_value)
                        
                        if metric_name == 'processing_time':
                            processing_time += metric_value
                    
                    elif metric_name in data_keys_overall:
                        key_dict.setdefault(metric_name, []).append(metric_value)
                        
                        # without tesseract..
                        if not key == 'tesseract':
                            schriftfarben_data[schriftfarbe].setdefault(metric_name, []).append(metric_value)
                            autoren_data[autor].setdefault(metric_name, []).append(metric_value)
                    
                    elif metric_name == 'machine_tuples':
                        machine_confidence_list.append(metric_value)
                    elif metric_name == 'handwritten_tuples':
                        handwritten_confidence_list.append(metric_value)
            
            blanko_data[key]['documents'][document_nr] = {
                doc_key: calc_average(values, len(values)) for doc_key, values in doc_dict.items()
            }
        
        blanko_data[key].update({
            key_dict_key: calc_average(values, len(values)) for key_dict_key, values in key_dict.items()
        })
        
        blanko_data[key]['processing_time'] = processing_time / 100
        
        blanko_data[key]['confidences'] = {
            'machine': machine_confidence_list,
            'handwritten': handwritten_confidence_list
        }
    
    schriftfarben_data_summ = {}
    for key_schriftfarbe, value_key in schriftfarben_data.items():
        schriftfarben_data_summ[key_schriftfarbe] = {}
        for act_key, act_value in value_key.items():
            schriftfarben_data_summ[key_schriftfarbe][act_key] = calc_average(act_value, len(act_value))
            
    autor_data_summ = {}
    for key_autor, value_key in autoren_data.items():
        autor_data_summ[key_autor] = {}
        for act_key, act_value in value_key.items():
            autor_data_summ[key_autor][act_key] = calc_average(act_value, len(act_value))

    summarized_data = {
        'other_data': {'schriftfarbe': schriftfarben_data_summ, 'autor': autor_data_summ},
        'data': blanko_data
    }

    return summarized_data

def save_summary_to_file(summary, output_path):
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def main():
    input_path = os.path.join('data', 'evaluatedData.json')
    output_path = os.path.join('data', 'summarizedData.json')

    with open(input_path, 'r', encoding="utf8") as f:
        data = json.load(f)
    
    data_keys_per_document = [
        'word_matches_machine', 'word_matches_handwritten', 'letter_matches_machine', 
        'letter_matches_handwritten', 'word_count_machine', 'word_count_handwritten', 
        'letter_count_machine', 'letter_count_handwritten', 'word_count_ocr_handwritten', 
        'word_count_ocr_machine', 'processing_time'
    ]
    blacklist = [
        'word_rebuilding_machine', 'word_splitting_machine', 
        'word_rebuilding_handwritten', 'word_splitting_handwritten', 'remaining_words'
    ]
    data_keys_overall = [
        "word_correct_machine", "letter_correct_machine", "word_correct_handwritten",
        "letter_correct_handwritten", "precision_machine", "recall_machine", "f1_machine", 
        "precision_handwritten", "recall_handwritten", "f1_handwritten"
    ]

    summary = summarize_metrics(data, data_keys_per_document, data_keys_overall, blacklist)
    save_summary_to_file(summary, output_path)

if __name__ == '__main__':
    main()

import os
import json

# class used by all ocr-tools to store the data into the files

class FileHandler:
    def __init__(self, logger, data_path):
        self._logger = logger
        self._data_path = data_path
        self._data = None

    @property
    def data(self):
        return self._data

    def handle_data(self, processed_word_data, document, exemplar, processingTime, pingBefore, pingAfter):
        """
        Saves processed data to a JSON file.
        """
        # save raw_data first
        raw_data_path = os.path.join(self._data_path, 'raw_data', str(document), f"{exemplar}.json")
        with open(raw_data_path, "w", encoding="utf8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=4)

        # Load existing data if the file exists
        processed_data_path = os.path.join(self._data_path, 'processedData.json')
        if os.path.exists(processed_data_path):
            with open(processed_data_path, "r", encoding="utf8") as f:
                processed_data = json.load(f)
        else:
            processed_data = {}

        # Add or update the data
        if not processed_data.get(str(document)):
            processed_data[str(document)] = {}

        processed_data[str(document)][str(exemplar)] = {
            "wordData": processed_word_data,
            "processingTime": processingTime,
            "pingBefore": pingBefore,
            "pingAfter": pingAfter
        }

        # Save the updated data back to the file
        with open(processed_data_path, "w", encoding="utf8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

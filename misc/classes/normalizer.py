import re

class OCRTextNormalizer:
    def __init__(self):
        # Definiere die Ersetzungen, die angewendet werden
        self.replacements = {
            r'[()/:,"]': " ",  # Ersetze (), / und : durch Leerzeichen
        }
        self.whitespace_pattern = r"\s+"  # Pattern für mehrfaches Leerzeichen
        self.date_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"  # Datumsmuster (z.B. 01.03.2023)

    def normalize(self, raw_text):
        """
        Normalisiert den Input (string oder Liste) anhand des Rule-Sets.
        Akzeptiert sowohl Strings als auch Listen von Wörtern.
        """
        if isinstance(raw_text, list):
            # Wenn Input eine Liste ist, verbinde die Wörter zu einem String
            raw_text = " ".join(raw_text)
        
        normalized_text = raw_text + " "
        for pattern, replacement in self.replacements.items():
            normalized_text = re.sub(pattern, replacement, normalized_text)
        
        # Entferne Punkte die vor Leerzeichen stehen
        normalized_text = re.sub(r"\.\s", " ", normalized_text)
        # Entferne Punkte nach Leerzeichen
        normalized_text = re.sub(r"\s\.", " ", normalized_text)

        # Reduziere mehrfaches Leerzeichen auf eines
        normalized_text = re.sub(self.whitespace_pattern, " ", normalized_text)

        # Trimme führende/trailing Whitespaces
        return normalized_text.strip().split(' ')




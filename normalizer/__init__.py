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
        return normalized_text.strip()

    def split_into_words(self, raw_text):
        """
        Zerlegt den Input in Wörter. Akzeptiert Strings oder Listen von Wörtern.
        """
        # Normalisiere zuerst den Text
        normalized_text = self.normalize(raw_text)
        # Teile den normalisierten Text in Wörter
        return normalized_text.split(" ")

    def reconstruct_date(self, date_parts):
        """
        Rekonstruiert ein Datum aus zerhackten Teilen (z.B. ['01', '03', '2023'] -> '01.03.2023').
        Überprüft, ob die Teile die richtige Anzahl und Formatierung haben.
        """
        if len(date_parts) == 3:
            # Falls drei Teile vorhanden sind (Tag, Monat, Jahr), füge sie zusammen
            return f"{date_parts[0]}.{date_parts[1]}.{date_parts[2]}"
        return None

# Test der Klasse
if __name__ == "__main__":
    raw_text_string = """
    Am 01. 03 .2023 wurde folgendes notiert: "Schneider / des Sdaner. 03.12.2001"
    """
    
    raw_text_list = [
        "Am", "01.", "03.", "2023", "wurde", "folgendes", "notiert:", "Schneider", "/", "des", "Sdaner.", "03.12.2001"
    ]
    expected_date = "01.03.2023"

    normalizer = OCRTextNormalizer()

    # String-Input
    print("String Input:")
    normalized_text = normalizer.normalize(raw_text_string)
    print("Normalisierter Text:", normalized_text)

    words = normalizer.split_into_words(raw_text_string)
    print("Wörter:", words)

    # Listen-Input
    print("\nListen Input:")
    normalized_text = normalizer.normalize(raw_text_list)
    print("Normalisierter Text:", normalized_text)

    words = normalizer.split_into_words(raw_text_list)
    print("Wörter:", words)



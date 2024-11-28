class Result:
    def __init__(self, data: dict):
        self.__data = data

    def __getattr__(self, name):
        if name in self.__data:
            return self.__data[name]
        raise AttributeError(f"'Result' object has no attribute '{name}'")

    def as_dict(self):
        # basierend auf den daten
        result = self.__data.copy()
        
        # alle attribute und properties prüfen
        for name in dir(self):
            # überspringe interne oder private attribute
            if name.startswith("_"):
                continue
            # prüfe, ob das attribut eine property ist
            attr = getattr(self.__class__, name, None)
            if isinstance(attr, property):
                result[name] = getattr(self, name)
        
        return result

    @property
    def word_correct_machine(self):
        return self.word_matches_machine / self.word_count_machine
    
    @property
    def letter_correct_machine(self):
        return self.letter_matches_machine / self.letter_count_machine
    
    @property
    def word_correct_handwritten(self):
        return self.word_matches_handwritten / self.word_count_handwritten
    
    @property
    def letter_correct_handwritten(self):
        return self.letter_matches_handwritten / self.letter_count_handwritten
    
    @property
    def precision_machine(self):
        tp = self.word_matches_machine
        fp = self.word_count_machine - tp
        return tp / (tp + fp) if (tp + fp) != 0 else 0

    @property
    def recall_machine(self):
        tp = self.word_matches_machine
        fn = self.word_count_machine - tp
        return tp / (tp + fn) if (tp + fn) != 0 else 0

    @property
    def f1_machine(self):
        precision = self.precision_machine
        recall = self.recall_machine
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    
    @property
    def precision_handwritten(self):
        tp = self.word_matches_handwritten
        fp = self.word_count_handwritten - tp
        return tp / (tp + fp) if (tp + fp) != 0 else 0

    @property
    def recall_handwritten(self):
        tp = self.word_matches_handwritten
        fn = self.word_count_handwritten - tp
        return tp / (tp + fn) if (tp + fn) != 0 else 0

    @property
    def f1_handwritten(self):
        precision = self.precision_handwritten
        recall = self.recall_handwritten
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

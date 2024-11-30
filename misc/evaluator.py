from misc.result import Result

@staticmethod
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class Evaluator:
    def __init__(self, machine_list, handwritten_list):
        self.machine_list = machine_list
        self.handwritten_list = handwritten_list

    def run(self, recognized_words: list[dict]):
        """
        vergleicht erkannte wörter mit maschinen- und handgeschriebenen listen,
        zählt übereinstimmungen und rekonstruiert wörter aus unvollständigen matches.
        
        Args:
            recognized_words (list[str]): liste erkannter wörter, die verarbeitet werden sollen.

        Returns:
            Result: objekt mit details zu wörter-matches, buchstaben-matches, rekonstruktionen und splits.
        """
        def process_list(target_list, word_rebuilding, word_splitting, letter_matches, confidence_tuples, word_count_ocr):
            """
            verarbeitet eine liste (machine oder handwritten), gleicht wörter ab, 
            versucht rekonstruktionen oder splits und aktualisiert buchstaben-matches.

            Args:
                target_list (list): die liste, die verarbeitet wird.
                word_rebuilding (dict): speichert rekonstruktionen für nicht exakte matches.
                word_splitting (dict): speichert informationen über wörter, die aufgeteilt wurden.
                letter_matches (int): zähler für erfolgreich gematchte buchstaben.
                confidence_tuples (list): tuple aus 0, confidence
                word_count_ocr (int): zähler wie viele wörter das ocr insgesamt erkannt hat

            Returns:
                int: aktualisierte buchstaben-matches.
            """
            i = 0
            while i < len(target_list):
                start_idx, end_idx, distance = self.check_remaining(target_list[i], recognized_words)

                if start_idx == -1 or end_idx == -1:
                    i += 1
                    continue

                # das gematchte snippet zusammensetzen
                matched_snippet = ""
                for k in range(start_idx, end_idx + 1):
                    matched_snippet += recognized_words[k]['word']

                # prüfe, ob ein zweiter Check nötig ist
                if distance > len(target_list[i]) // 3:
                    start_idx_2, end_idx_2, distance_2 = self.check_remaining(
                        matched_snippet, target_list, use_spacing=True
                    )
                    
                    # Hier passiert folgendes:
                    # das OCR-Tool erkennt ein einziges Wort, vorgegeben waren aber mehrere, also:
                    # OCR-erkannt: 'daraufbefindlichen', eigentliche Wörter 'darauf', 'befindlichen'

                    if distance_2 != -1 and distance_2 < distance:
                        distance = distance_2
                        
                        # Wort rekonstruieren
                        word = target_list[start_idx_2:end_idx_2 + 1]
                        if matched_snippet in word_splitting:
                            word_splitting[matched_snippet].append(word)
                        else:
                            word_splitting[matched_snippet] = [word]

                        # Buchstaben addieren
                        letter_matches += len(matched_snippet) - distance
                        
                        # Löschen aus Target-List und Recognized-Words
                        del target_list[start_idx_2:end_idx_2 + 1]
                        for j in range(len(recognized_words)):
                            if recognized_words[j].get('word') == matched_snippet:
                                # Confidence aus dem Loop holen, schont Ressourcen..
                                confidence = recognized_words[j].get('confidence')
                                recognized_words.pop(j)
                                break
                        
                        # Confidence appenden (für jedes der vorgegeben Wörter "Schnipsel" den einen Wert des vom OCR
                        # erkannten Wortes)
                        for _ in range(end_idx_2-start_idx_2+1):
                            confidence_tuples.append((0, confidence))
                        
                        # Wörter-Count einen hoch
                        word_count_ocr+=1
                                
                        i += end_idx_2 - start_idx_2 - 1
                        continue

                # Hier passiert folgendes:
                # das OCR-Tool erkennt mehrere Wörter, vorgegeben war aber eins, also:
                # OCR-erkannt: '01', '03', '2023', eigentliches Wort war aber '01.03.2023'
                if matched_snippet not in word_splitting:
                    # Wort rekonstruieren und Confidence zusammenrechnen
                    matched_snippet = ""
                    confidence = 0
                    for k in range(start_idx, end_idx + 1):
                        # Schnipsel zusammensetzen, Confidence addieren, und Wörter-Count vom OCR hochzählen
                        matched_snippet += recognized_words[k]['word']
                        confidence += recognized_words[k]['confidence']
                        word_count_ocr+=1
                    
                    # hier wird die confidence durch die anzahl der wortschnipsel geteilt, quasi als "durchschnitt"
                    confidence_norm = confidence / (end_idx - start_idx + 1)
                        
                    # Zusammensetzung speichern, falls schon vorhanden als liste
                    if target_list[i] in word_rebuilding:
                        word_rebuilding[target_list[i]].append(matched_snippet)
                    else:
                        word_rebuilding[target_list[i]] = [matched_snippet]
                    
                    # Buchstaben addieren
                    letter_matches += len(target_list[i]) - distance
                    
                    # Confidence-Werte appenden
                    confidence_tuples.append((0, confidence_norm))
                    
                    # Löschen des erkannten Wortes aus Recognized-Words und pop() des gematchten aus target-list
                    del recognized_words[start_idx:end_idx + 1]
                    target_list.pop(i)

            return letter_matches, confidence_tuples, word_count_ocr

        # Init Variablen
        letter_count_machine = sum(len(word) for word in self.machine_list)
        letter_count_handwritten = sum(len(word) for word in self.handwritten_list)

        # init maschinen variablen
        word_matches_machine = 0
        letter_matches_machine = 0
        word_rebuilding_machine = {}
        word_splitting_machine = {}
        machine_tuples = []

        # init handwritten variablen
        word_matches_handwritten = 0
        letter_matches_handwritten = 0
        word_rebuilding_handwritten = {}
        word_splitting_handwritten = {}
        handwritten_tuples = []

        machine_list = self.machine_list.copy()
        handwritten_list = self.handwritten_list.copy()

        # Iteration über recog words
        index = 0
        while index < len(recognized_words):
            word = recognized_words[index]['word']
            if word in machine_list:
                word_matches_machine += 1
                letter_matches_machine += len(word)
                machine_tuples.append((1, recognized_words[index]['confidence']))
                
                # remove from lists
                recognized_words.pop(index)
                machine_list.remove(word)
            elif word in handwritten_list:
                word_matches_handwritten += 1
                letter_matches_handwritten += len(word)
                handwritten_tuples.append((1, recognized_words[index]['confidence']))
                
                # remove from lists
                recognized_words.pop(index)
                handwritten_list.remove(word)
            else:
                index += 1
        
        # Zählen der vom OCR erkannten Worte
        # müssen dann addiert = len(recognized_words) sein
        # Für die Berechnung von False Positives
        word_count_ocr_machine = word_matches_machine
        word_count_ocr_handwritten= word_matches_handwritten

        # für alle nicht 100% korrekt erkannten wörter
        letter_matches_handwritten, handwritten_tuples, word_count_ocr_handwritten = process_list(
            handwritten_list,
            word_rebuilding_handwritten,
            word_splitting_handwritten,
            letter_matches_handwritten,
            handwritten_tuples,
            word_count_ocr_handwritten
        )

        letter_matches_machine, machine_tuples, word_count_ocr_machine = process_list(
            machine_list,
            word_rebuilding_machine,
            word_splitting_machine,
            letter_matches_machine,
            machine_tuples,
            word_count_ocr_machine
        )
        
        # falls jetzt noch etwas in den recognized_words ist -> zusätzlich erkanntes wort
        # konnte nicht zugeordnet werden.
        if recognized_words:
            if handwritten_list and not machine_list:
                word_count_ocr_handwritten += len(recognized_words)
            
            if machine_list and not handwritten_list:
                word_count_ocr_machine += len(recognized_words)
                
            # falls hier noch was in recognized_words ist, dann ist es wahrscheinlich handgeschriebener text.
            if not machine_list and not handwritten_list:
                word_count_ocr_handwritten += len(recognized_words)
            
            # schwierig? abwechselnde zuordnung zu handwritten und machine..
            if machine_list and handwritten_list:
                for i in range(len(recognized_words)):
                    if not i % 2:
                        word_count_ocr_handwritten += 1
                    else:
                        word_count_ocr_machine += 1

        # Result-Daten zusammenfassen
        result_data = {
            "word_matches_machine": word_matches_machine,
            "word_matches_handwritten": word_matches_handwritten,
            "letter_matches_machine": letter_matches_machine,
            "letter_matches_handwritten": letter_matches_handwritten,
            "word_count_machine": len(self.machine_list),
            "word_count_handwritten": len(self.handwritten_list),
            "letter_count_machine": letter_count_machine,
            "letter_count_handwritten": letter_count_handwritten,
            "word_rebuilding_machine": word_rebuilding_machine,
            "word_splitting_machine": word_splitting_machine,
            "word_rebuilding_handwritten": word_rebuilding_handwritten,
            "word_splitting_handwritten": word_splitting_handwritten,
            "remaining_words": recognized_words,
            "machine_tuples": machine_tuples,
            "handwritten_tuples": handwritten_tuples,
            "word_count_ocr_handwritten": word_count_ocr_handwritten,
            "word_count_ocr_machine": word_count_ocr_machine
        }

        return Result(result_data)


    def check_remaining(self, word: str, word_list: list[dict], use_spacing=False):
        """
        Rekonstruiert ein wort und gibt die minimaldistanz sowie die indices des besten matches zurück.

        Args:
            word (str): Das zu rekonstruierende wort.
            word_list (list[str]): Liste der vermeintlichen wortschnipsel.
            use_spacing (bool): verwendet falls das erkannte wort aus mehreren schnipseln besteht (zur 
                                Distanz werden dann zusätzliche Leerzeichen addiert)

        Returns:
            tuple: (start_idx, end_idx, min_distance)
        """
        min_distance = float('inf')
        min_spacing = 0
        best_indices = (-1, -1)
        map = {}

        threshold = len(word) // 1.5

        for start_idx in range(len(word_list)):
            current_concat = ""
            previous_distance = float('inf')
            spacing_counter = 0

            for end_idx in range(start_idx, len(word_list)):
                if isinstance(word_list[end_idx], dict):
                    current_concat += word_list[end_idx]['word']
                else:
                    current_concat += word_list[end_idx]
                distance = levenshtein_distance(word, current_concat)

                map[current_concat] = distance

                if distance > previous_distance:
                    break

                previous_distance = distance

                if distance < min_distance:
                    min_spacing = spacing_counter
                    min_distance = distance
                    best_indices = (start_idx, end_idx)

                spacing_counter += 1

        if use_spacing:
            min_distance = min_distance + min_spacing

        if min_distance > threshold:
            return (-1, -1, -1)

        return (*best_indices, min_distance)

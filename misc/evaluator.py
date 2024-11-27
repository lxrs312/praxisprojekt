# hier werden ganz böse dinge geschehen...
from collections import defaultdict
import os
import json

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



class Result:
    def __init__(self, word_matches_machine, word_matches_handwritten, letter_matches_machine, letter_matches_handwritten, 
                 word_count_machine, word_count_handwritten, letter_overall_machine, letter_overall_handwritten):
        self.__word_matches_machine = word_matches_machine
        self.__word_count_machine = word_count_machine
        self.__word_matches_handwritten = word_matches_handwritten
        self.__word_count_handwritten = word_count_handwritten

        self.__letter_matches_machine = letter_matches_machine
        self.__letter_overall_machine = letter_overall_machine
        self.__letter_matches_handwritten = letter_matches_handwritten
        self.__letter_overall_handwritten = letter_overall_handwritten

    @property
    def word_matches_machine(self):
        return self.__word_matches_machine

    @property
    def word_matches_handwritten(self):
        return self.__word_matches_handwritten

    @property
    def letter_matches_machine(self):
        return self.__letter_matches_machine

    @property
    def letter_matches_handwritten(self):
        return self.__letter_matches_handwritten

    @property
    def word_count_machine(self):
        return self.__word_count_machine

    @property
    def word_count_handwritten(self):
        return self.__word_count_handwritten

    @property
    def letter_overall_machine(self):
        return self.__letter_overall_machine

    @property
    def letter_overall_handwritten(self):
        return self.__letter_overall_handwritten

    def as_dict(self):
        return {
            "word_matches_machine": self.word_matches_machine,
            "word_matches_handwritten": self.word_matches_handwritten,
            "letter_matches_machine": self.letter_matches_machine,
            "letter_matches_handwritten": self.letter_matches_handwritten,
            "word_count_machine": self.word_count_machine,
            "word_count_handwritten": self.word_count_handwritten,
            "letter_overall_machine": self.letter_overall_machine,
            "letter_overall_handwritten": self.letter_overall_handwritten,
        }


class Evaluator:
    def __init__(self, machine_list, handwritten_list):
        self.machine_list = machine_list
        self.handwritten_list = handwritten_list

    def run(self, recognized_words: list[str]):
        # init variablen für machine-list
        word_matches_machine = 0
        letter_matches_machine = 0
        letter_overall_machine = sum(len(word) for word in self.machine_list)
        word_count_machine = len(self.machine_list)
     
        # init variablen für letter-list   
        word_matches_handwritten = 0
        letter_matches_handwritten = 0
        letter_overall_handwritten = sum(len(word) for word in self.handwritten_list)
        word_count_handwritten = len(self.handwritten_list)

        # copy lists for iteration
        machine_list = self.machine_list.copy()
        handwritten_list = self.handwritten_list.copy()

        # iterate through each recognized word
        # iteriere direkt über recognized_words
        index = 0
        while index < len(recognized_words):
            word = recognized_words[index]
            if word in machine_list:
                word_matches_machine += 1
                letter_matches_machine += len(word)
                recognized_words.pop(index)  # lösche das Wort aus recognized_words
                machine_list.remove(word)
            elif word in handwritten_list:
                word_matches_handwritten += 1
                letter_matches_handwritten += len(word)
                recognized_words.pop(index)
                handwritten_list.remove(word)
            else:
                index += 1

        print('Machine-List:', machine_list)
        print('Handwritten-List:', handwritten_list)

        for remaining in handwritten_list:
            start_idx, end_idx, distance = self.check_remaining(remaining, recognized_words)
            if start_idx != -1 and end_idx != -1:
                matched_snippet = ''.join(recognized_words[start_idx:end_idx + 1])

                start_idx_2, end_idx_2, distance_2 = self.check_remaining(matched_snippet, handwritten_list)
                matched_snippet_2 = ''.join(handwritten_list[start_idx_2:end_idx_2 + 1])

                # updates
                letter_matches_handwritten += len(remaining) - distance

                # entfernen der verwendeten schnipsel
                del recognized_words[start_idx:end_idx + 1]

        # check die remaining wörter in machine/handwritten list und levensthein 
        for remaining in machine_list:
            start_idx, end_idx, distance = self.check_remaining(remaining, recognized_words)
            if start_idx != -1 and end_idx != -1:
                matched_snippet = ''.join(recognized_words[start_idx:end_idx + 1])

                print(matched_snippet, distance)

                # Check if distance is high enough for another check
                if not distance < len(remaining) // 3:
                    start_idx_2, end_idx_2, distance_2 = self.check_remaining(matched_snippet, machine_list)
                    matched_snippet_2 = ''.join(machine_list[start_idx_2:end_idx_2 + 1])

                    if distance_2 < distance:
                        print(matched_snippet_2, distance_2)

                # updates
                letter_matches_machine += len(remaining) - distance

                # entfernen der verwendeten schnipsel
                del recognized_words[start_idx:end_idx + 1]

        return Result(word_matches_machine, word_matches_handwritten, letter_matches_machine, letter_matches_handwritten,
                        word_count_machine, word_count_handwritten, letter_overall_machine, letter_overall_handwritten)


    def check_remaining(self, remaining_word: str, remaining_recognized_list: list[str]):
        """
        Rekonstruiert ein wort und gibt die minimaldistanz sowie die indices des besten matches zurück.

        Args:
            remaining_word (str): Das zu rekonstruierende wort.
            remaining_recognized_list (list[str]): Liste der übrigen wortschnipsel.

        Returns:
            tuple: (start_idx, end_idx, min_distance)
        """
        min_distance = float('inf')
        min_spacing = 0
        best_indices = (-1, -1)
        map = {}

        threshold = len(remaining_word) // 2

        for start_idx in range(len(remaining_recognized_list)):
            current_concat = ""
            previous_distance = float('inf')
            spacing_counter = 0

            for end_idx in range(start_idx, len(remaining_recognized_list)):
                current_concat += remaining_recognized_list[end_idx]
                distance = levenshtein_distance(remaining_word, current_concat)

                map[current_concat] = distance

                if distance > previous_distance:
                    break

                previous_distance = distance

                if distance < min_distance:
                    min_spacing = spacing_counter
                    min_distance = distance
                    best_indices = (start_idx, end_idx)

                spacing_counter += 1

        min_distance = min_distance + min_spacing

        if min_distance > threshold:
            return (-1, -1, -1)

        return (*best_indices, min_distance)

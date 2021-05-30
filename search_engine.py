from bisect import bisect_left
from openpyxl import load_workbook
import re
import numpy as np
import pickle


class SearchEngine:

    def _load_documents(self):

        wb = load_workbook("./input_data/IR_Spring2021_ph12_7k.xlsx")
        sheet = wb.active

        self.content_list = []
        self.url_list = []

        for i in range(2, 7002):
            data_id = int(sheet.cell(i, 1).value)
            data_content = sheet.cell(i, 2).value
            data_url = sheet.cell(i, 3).value
            self.content_list.append(data_content)
            self.url_list.append(data_url)

    def _load_lemmatize(self):
        file = open("./input_data/lemmatize")
        self.lemmatize = []
        for line in file.readlines():
            past, present = line.split(" ")
            self.lemmatize.append({"past": past, "present": present})

    def _load_mokassar(self):
        file = open("./input_data/mokassar")
        self.mokassar = []
        for line in file.readlines():
            plural, single = line.split(" ")
            self.mokassar.append({"plural": plural, "single": single})

    @staticmethod
    def _preprocess_remove_redundant_symbol(text):
        text = re.sub('\.', ' ', text)
        text = re.sub('،', ' ', text)
        text = re.sub(',', ' ', text)
        text = re.sub('\n', ' ', text)
        text = re.sub(':', ' ', text)
        text = re.sub('؛', ' ', text)
        text = re.sub('"', ' ', text)
        text = re.sub('“', ' ', text)
        text = re.sub('”', ' ', text)
        text = re.sub('\(', ' ', text)
        text = re.sub('\)', ' ', text)
        text = re.sub('\]', ' ', text)
        text = re.sub('\[', ' ', text)
        text = re.sub('-', ' ', text)
        text = re.sub('\*', ' ', text)
        text = re.sub('«', ' ', text)
        text = re.sub('»', ' ', text)
        text = re.sub('؟', ' ', text)
        text = re.sub('\?', ' ', text)
        text = re.sub('/', ' ', text)
        text = re.sub('!', ' ', text)
        text = re.sub('-', ' ', text)
        text = re.sub('–', ' ', text)
        text = re.sub('ـ', ' ', text)
        text = re.sub('_', ' ', text)
        text = re.sub('…', ' ', text)

        text = re.sub(u"\u064D", ' ', text)
        text = re.sub(u"\u0650", ' ', text)
        text = re.sub(u"\u064B", ' ', text)
        text = re.sub(u"\u064E", ' ', text)
        text = re.sub(u"\u064C", ' ', text)
        text = re.sub(u"\u0651", ' ', text)

        text = re.sub(r' +', ' ', text)
        return text

    @staticmethod
    def _preprocess_equalize(text):
        text = re.sub("ك", "ک", text)
        text = re.sub("اً", "ا", text)
        text = re.sub("أ", "ا", text)
        text = re.sub("ؤً", "و", text)
        text = re.sub("ة", "ه", text)
        text = re.sub("ي", "ی", text)

        text = re.sub("1", "۱", text)
        text = re.sub("2", "۲", text)
        text = re.sub("3", "۳", text)
        text = re.sub("4", "۴", text)
        text = re.sub("5", "۵", text)
        text = re.sub("6", "۶", text)
        text = re.sub("7", "۷", text)
        text = re.sub("8", "۸", text)
        text = re.sub("9", "۹", text)
        text = re.sub("0", "۰", text)
        return text

    @staticmethod
    def preprocess(text):
        text = SearchEngine._preprocess_remove_redundant_symbol(text)
        text = SearchEngine._preprocess_equalize(text)
        return text

    def _mine_tokens(self):
        self.tokens_list = []

        for content in self.content_list:
            text = content
            text = self.preprocess(text)

            tokens = re.split(" ", text)
            self.tokens_list.append(tokens)

    @staticmethod
    def _normalize_remove_postfix(token):
        token = re.sub(r" *تر$", "", token)
        token = re.sub(r" *ترین$", "", token)
        token = re.sub(r" *ها$", "", token)
        token = re.sub(r" *های$", "", token)
        token = re.sub(r" *ات$", "", token)
        token = re.sub(u"\u200c" + r"$", "", token)
        return token

    @staticmethod
    def _normalize_remove_prefix(token):
        token = re.sub(r"^می", "", token)
        token = re.sub(r"^" + u"\u200c", "", token)
        token = re.sub(r"^" + u"\u200f", "", token)
        return token

    def _normalize_lemmatize(self, token):
        for item in self.lemmatize:
            past = item["past"]
            present = item["present"]
            infinitive = past + "ن"

            past_postfix = ["م", "یم", "ی", "ید", "", "ند"]
            present_postfix = ["م", "یم", "ی", "ید", "د", "ند"]

            for postfix in past_postfix:
                verb = past + postfix
                if verb == token:
                    return infinitive

            for postfix in present_postfix:
                verb = present + postfix
                if verb == token:
                    return infinitive

        return token

    def _normalize_mokassar(self, token):
        for item in self.mokassar:
            if token == item["plural"]:
                return item["single"]

        return token

    def normalize(self, token):
        token = self._normalize_remove_prefix(token)
        token = self._normalize_remove_postfix(token)
        token = self._normalize_lemmatize(token)
        token = self._normalize_mokassar(token)
        return token

    def _normalize_tokens(self):
        new_token_list = []
        for tokens in self.tokens_list:
            new_tokens = []
            for token in tokens:
                token = self.normalize(token)
                new_tokens.append(token)
            new_token_list.append(new_tokens)
        self.tokens_list = new_token_list

    def _find_stop_words(self):
        all_words = []
        for tokens in self.tokens_list:
            all_words += tokens

        values, counts = np.unique(all_words, return_counts=True)
        self.stop_words_threshold = 1000
        self.stop_words = []

        for i in range(len(values)):
            if counts[i] > self.stop_words_threshold:
                self.stop_words.append(values[i])

        self.stop_words = set(self.stop_words)

    def _aggregate_inverted_index(self):
        term_doc_list = []
        for i, tokens in enumerate(self.tokens_list):
            unique_tokens_list = set(tokens)
            unique_tokens_list -= self.stop_words
            for word in unique_tokens_list:
                term_doc_list.append({'term': word, 'doc': i + 1})

        sorted_term_doc_list = sorted(term_doc_list, key=lambda x: x["term"])

        self.inverted_index = []
        previous_term = None
        for term_doc in sorted_term_doc_list:
            current_term = term_doc["term"]
            doc_id = term_doc["doc"]
            if previous_term != current_term:
                self.inverted_index.append({"term": current_term, "docs": []})
            self.inverted_index[-1]["docs"].append(doc_id)

            previous_term = current_term

    def _save_inverted_index(self):
        with open('./output_data/inverted_index', 'wb') as fp:
            pickle.dump(self.inverted_index, fp)
        with open('./output_data/dictionary', 'wb') as fp:
            pickle.dump(self.dictionary, fp)

    def load_inverted_index(self):
        self._load_documents()
        self._load_lemmatize()
        self._load_mokassar()
        with open('./output_data/inverted_index', 'rb') as fp:
            self.inverted_index = pickle.load(fp)
        with open('./output_data/dictionary', 'rb') as fp:
            self.dictionary = pickle.load(fp)

    def get_documents(self, word):
        word = self.preprocess(word)
        word = re.sub(" ", "", word)
        word = self.normalize(word)
        print(word)
        i = bisect_left(self.dictionary, word)
        if i != len(self.dictionary) and word == self.dictionary[i]:
            return self.inverted_index[i]
        else:
            return None

    def _create_dictionary(self):
        self.dictionary = []
        for x in self.inverted_index:
            self.dictionary.append(x["term"])
            # if len(x["docs"]) > 10:
            print(x["term"])

    def create_inverted_index(self):
        self._load_documents()
        self._load_lemmatize()
        self._load_mokassar()
        self._mine_tokens()
        self._normalize_tokens()
        self._find_stop_words()
        self._aggregate_inverted_index()
        self._create_dictionary()
        self._save_inverted_index()

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

    def _mine_tokens(self):
        self.tokens_list = []

        for content in self.content_list:
            text = content
            text = re.sub('\.', ' ', text)
            text = re.sub('،', ' ', text)
            text = re.sub(',', ' ', text)
            text = re.sub('\n', ' ', text)
            text = re.sub(':', ' ', text)
            text = re.sub('؛', ' ', text)
            text = re.sub('"', ' ', text)
            text = re.sub('\(', ' ', text)
            text = re.sub('\)', ' ', text)
            text = re.sub('\]', ' ', text)
            text = re.sub('\[', ' ', text)
            text = re.sub('-', ' ', text)
            text = re.sub('\*', ' ', text)
            text = re.sub('«', ' ', text)
            text = re.sub('»', ' ', text)

            text = re.sub(r' +', ' ', text)

            tokens = re.split(" ", text)
            # sorted_tokens = sorted(tokens)
            self.tokens_list.append(tokens)

    def _normalize(self):
        pass

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

        # sorted_term_doc_list = sorted(term_doc_list, key=lambda x: x["term"])

        self.inverted_index = []
        previous_term = None
        for term_doc in term_doc_list:
            current_term = term_doc["term"]
            doc_id = term_doc["doc"]
            if previous_term != current_term:
                self.inverted_index.append({"term": current_term, "docs": []})

                self.inverted_index[-1]["docs"].append(doc_id)

    def _save_inverted_index(self):
        with open('inverted_index', 'wb') as fp:
            pickle.dump(self.inverted_index, fp)

    def load_inverted_index(self):
        with open('inverted_index', 'rb') as fp:
            self.inverted_index = pickle.load(fp)

    def get_documents(self, word):
        return self.inverted_index[word]

    def create_inverted_index(self):
        self._load_documents()
        self._mine_tokens()
        self._normalize()
        self._find_stop_words()
        self._aggregate_inverted_index()
        self._save_inverted_index()

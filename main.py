from search_engine import SearchEngine

searchEngine = SearchEngine()

searchEngine._load_lemmatize()

# searchEngine.create_inverted_index()
# searchEngine.load_inverted_index()

# print()
# print(searchEngine.get_documents("مازوت"))

# token = "رفتند"
# print(searchEngine._normalize_lemmatize(token))
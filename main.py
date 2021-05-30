from search_engine import SearchEngine

searchEngine = SearchEngine()

# searchEngine.create_inverted_index()
searchEngine.load_inverted_index()

# print()

searchEngine.search("میدانdd")

# token = "رفتند"
# print(searchEngine._normalize_lemmatize(token))
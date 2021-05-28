from search_engine import SearchEngine

searchEngine = SearchEngine()

searchEngine.create_inverted_index()
# searchEngine.load_inverted_index()

# print()
# print(searchEngine.get_documents("مازوت"))

token = "می‌خورد"
print(searchEngine.normalize(token))
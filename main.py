from search_engine import SearchEngine

searchEngine = SearchEngine()

# searchEngine.create_inverted_index()
searchEngine.load_inverted_index()

print(searchEngine.get_documents("نهاد"))
print(searchEngine.get_documents("نهاد‌های"))

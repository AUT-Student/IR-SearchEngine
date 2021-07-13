from search_engine import SearchEngine

searchEngine = SearchEngine()

# searchEngine.create_inverted_index()
searchEngine.load_inverted_index()
searchEngine.evaluate_nearest_neighbours()

print("Ready...")
while True:
    query = input()
    if query == "Exit":
        break
    else:
        searchEngine.search(query)

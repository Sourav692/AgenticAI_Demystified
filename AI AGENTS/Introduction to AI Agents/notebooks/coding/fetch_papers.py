# filename: fetch_papers.py

import requests

def fetch_papers(query, limit=5):
    # The Semantic Scholar API for searching papers
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,abstract,authors'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        papers = response.json().get('data', [])
        return papers
    else:
        print(f"Failed to fetch papers: {response.status_code}")
        return []

def main():
    query = "large language models human productivity"
    papers = fetch_papers(query)
    
    if papers:
        for i, paper in enumerate(papers):
            title = paper.get('title')
            abstract = paper.get('abstract')
            authors = ", ".join([author['name'] for author in paper.get('authors', [])])
            
            print(f"Paper {i+1}:")
            print(f"Title: {title}")
            print(f"Abstract: {abstract}")
            print(f"Authors: {authors}")
            print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    main()
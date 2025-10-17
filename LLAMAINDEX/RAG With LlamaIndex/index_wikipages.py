# REPLACE THIS WITH YOUR CODE

# define the data model in pydantic
class WikiPageList(BaseModel):
    "Data model for WikiPageList"
    pages: # REPLACE THIS WITH YOUR CODE


def wikipage_list(query):
    openai.api_key = # REPLACE THIS WITH YOUR CODE

    # REPLACE THIS WITH YOUR CODE

    wikipage_requests = program(query=query)

    return wikipage_requests


def create_wikidocs(wikipage_requests):
    # REPLACE THIS WITH YOUR CODE
    
    return documents


def create_index(query):
    global index
    # REPLACE THIS WITH YOUR CODE

    return index


if __name__ == "__main__":
    query = "/get wikipages: paris, lagos, lao"
    index = create_index(query)
    print("INDEX CREATED", index)

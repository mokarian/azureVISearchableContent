import sys
from client.searchClient import SearchClient

if __name__ == "__main__":
    SEARCH_CLIENT = SearchClient()
    #  step 1
    SEARCH_CLIENT.create_index()
    #  step 2
    if sys.argv and sys.argv[0] == "local":
        SEARCH_CLIENT.upload_local_files_to_search()
    else:
        SEARCH_CLIENT.upload_files_from_storage_to_search()

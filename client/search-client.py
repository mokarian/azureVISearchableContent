import json
import os

import requests

from VIIntervalParser.client.clientabstract import ClientAbstract
from VIIntervalParser.parser.parser import Parser


class SearchClient(ClientAbstract):
    def __init__(self):
        self.endpoint = "https://" + self.config["search"]["service-name"] + ".search.windows.net/"
        self.api_version = "?api-version=" + self.config["search"]["api-version"]
        self.headers = {'Content-Type': 'application/json',
                        'api-key': self.config["search"]["api-key"]}

    def upload_to_search(self, docs):
        url = self.endpoint + "indexes/" + self.config["search"]["index-name"] + "/docs/index" + self.api_version
        response = requests.post(url, headers=self.headers, json=docs)
        index_content = response.json()
        print(index_content)

    def create_index(self):
        url = self.endpoint + "indexes" + self.api_version
        index_schema = self.read_file_from_directory("index-schema.json")
        index_schema["name"] = self.config["search"]["index-name"]
        response = requests.post(url, headers=self.headers, json=index_schema)
        response = response.json()
        print(response)

    @staticmethod
    def upload_local_files_to_search():
        files = SEARCH_CLIENT.read_files_from_directory(SEARCH_CLIENT.config["files"]["download-blob-directory"])
        i = 0
        for file in files:
            path = os.path.join(SEARCH_CLIENT.config["files"]["download-blob-directory"], file)
            i += 1
            with open(path) as f:
                try:
                    json_object = json.load(f)
                    if json_object["state"] == "Processed":
                        parser = Parser()
                        intervals = parser.parse_vi_json(json_object)
                        intervals = list(intervals.values())
                        for item in intervals:
                            item["@search.action"] = "upload"

                        documents = {
                            "value": intervals}
                        print(str(i) + ": uploading to search" + str(file))
                        SEARCH_CLIENT.upload_to_search(documents)
                        SEARCH_CLIENT.write_status_file(file, SEARCH_CLIENT.config["files"]["ingested-file"])
                except ValueError:
                    print("could not process " + str(file))
                    SEARCH_CLIENT.write_status_file(file, SEARCH_CLIENT.config["files"]["failed-to-ingest-file"])


if __name__ == "__main__":
    SEARCH_CLIENT = SearchClient()
    #  step 1
    SEARCH_CLIENT.create_index()
    #  step 2
    SEARCH_CLIENT.upload_local_files_to_search()

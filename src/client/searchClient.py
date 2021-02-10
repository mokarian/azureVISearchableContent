import json
import os

import requests

from client.clientabstract import ClientAbstract
from parser.parser import Parser
from client.storageClient import StorageClient


class SearchClient(ClientAbstract):
    def __init__(self):
        search_service_name = (
            self.config["search"]["service-name"]
            if self.config
            else os.getenv("SEARCH_SERVICE_NAME")
        )
        api_version = (
            self.config["search"]["api-version"]
            if self.config
            else os.getenv("SEARCH_API_VERSION")
        )
        search_api_key = (
            self.config["search"]["api-key"]
            if self.config
            else os.getenv("SEARCH_API_KEY")
        )

        self.endpoint = "https://" + search_service_name + ".search.windows.net/"
        self.api_version = "?api-version=" + api_version
        self.headers = {"Content-Type": "application/json", "api-key": search_api_key}
        self.storage_client = StorageClient()
        self.index_name = (
            self.config["search"]["index-name"]
            if self.config
            else os.getenv("SEARCH_INDEX_NAME")
        )
        self.index_schema_path = (
            self.config["search"]["index-schema-path"]
            if self.config
            else os.getenv("INDEX_SCHEMA_PATH")
        )
        self.insights_container = (
            self.config["storage"]["container"]
            if self.config
            else os.getenv("INSIGHTS_CONTAINER_NAME")
        )
        self.ingest_log_filename = (
            self.config["files"]["ingested-file"]
            if self.config
            else os.getenv("INGEST_LOG_FILENAME")
        )
        self.ingest_failure_log_filename = (
            self.config["files"]["failed-to-ingest-file"]
            if self.config
            else os.getenv("INGEST_FAILURE_LOG_FILENAME")
        )
        self.vi_output_directory = (
            self.config["files"]["vi-output-directory"]
            if self.config
            else os.getenv("VI_OUTPUT_DIRECTORY")
        )

    def upload_to_search(self, docs):
        url = (
            self.endpoint
            + "indexes/"
            + self.index_name
            + "/docs/index"
            + self.api_version
        )
        response = requests.post(url, headers=self.headers, json=docs)
        index_content = response.json()
        print(index_content)

    def create_index(self):
        url = self.endpoint + "indexes" + self.api_version
        index_schema = self.read_file_from_directory(self.index_schema_path)
        index_schema["name"] = self.index_name
        response = requests.post(url, headers=self.headers, json=index_schema)
        response = response.json()
        print(response)

    def upload_files_from_storage_to_search(self):
        print("uploading files from storage account to search")
        vi_output_files = self.storage_client.list_files_in_container(
            self.insights_container
        )
        i = 0
        for file in vi_output_files:
            i += 1
            try:
                json_object = json.loads(
                    self.storage_client.get_blob_string(
                        self.insights_container, file.name
                    ).encode()  # Encode as UTF-8 in case UTF-8 BOM
                )
                if json_object["state"] == "Processed":
                    parser = Parser()
                    intervals = parser.parse_vi_json(json_object)
                    intervals = list(intervals.values())
                    for item in intervals:
                        item["@search.action"] = "upload"

                    documents = {"value": intervals}
                    print(str(i) + f": uploading {str(file.name)} to search index")
                    self.upload_to_search(documents)
                    self.write_status_file(str(file.name), self.ingest_log_filename)
            except ValueError:
                print("could not process " + str(file))
                self.write_status_file(file, self.ingest_failure_log_filename)

    def upload_local_files_to_search(self):
        print("uploading local files to search")
        files = self.read_files_from_directory(self.vi_output_directory)
        i = 0
        for file in files:
            path = os.path.join(self.vi_output_directory, file)
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

                        documents = {"value": intervals}
                        print(str(i) + f": uploading {str(file)} to search index")
                        self.upload_to_search(documents)
                        self.write_status_file(file, self.ingest_log_filename)

                except ValueError:
                    print("could not process " + str(file))
                    self.write_status_file(file, self.ingest_failure_log_filename)

__author__ = 'Maysam Mokarian'
__email__ = "mamokari@microsoft.com"
__license__ = "MIT"
__version__ = "February 2022"

import os

from azure.storage.blob import BlobServiceClient

from client.clientabstract import ClientAbstract


class StorageClient(ClientAbstract):
    def __init__(self):

        connection_string = (
            self.config["storage"]["connection-string"]
            if self.config
            else os.getenv("STORAGE_CONNECTION_STRING")
        )
        insights_container_name = (
            self.config["storage"]["container"]
            if self.config
            else os.getenv("INSIGHTS_CONTAINER_NAME")
        )

        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            insights_container_name
        )

    def read_files_from_container_to_local(self):
        # TODO: this function is not used except for manual testing in the main function of this file. Refactor.
        blob_list = self.container_client.list_blobs()

        for blob in blob_list:

            download_file_path = os.path.join(
                self.config["files"]["download-blob-directory"], blob.name
            )
            if not os.path.exists(download_file_path):
                print("\nDownloading blob to \n\t" + download_file_path)

                blob_client = self.blob_service_client.get_blob_client(
                    container=self.config["storage"]["container"], blob=blob.name
                )

                with open(download_file_path, "wb") as my_blob:
                    my_blob.writelines([blob_client.download_blob().readall()])

    def list_files_in_container(self, container, name_starts_with=None):
        """
        this method list all the files in a container
        :param container:
        :return:
        """
        container_client = self.blob_service_client.get_container_client(container)
        return container_client.list_blobs(name_starts_with=name_starts_with)

    def get_blob_string(self, container, blob):
        try:
            return (
                self.blob_service_client.get_blob_client(container, blob)
                .download_blob()
                .readall()
            ).decode("utf-8")
        except Exception as ex:
            print(
                "Could not read the content of blob:{} in container:{}\n "
                "or the content could not be decoded to string "
                ", \nerror:{}".format(blob, container, ex)
            )


if __name__ == "__main__":
    CLIENT = StorageClient()
    CLIENT.read_files_from_container_to_local()

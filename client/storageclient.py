import os

from azure.storage.blob import BlobServiceClient

from client.clientabstract import ClientAbstract


class StorageClient(ClientAbstract):
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(self.config["storage"]["connection-string"])
        self.container_client = self.blob_service_client.get_container_client(self.config["storage"]["container"])

    def read_files_from_container_to_local(self):
        blob_list = self.container_client.list_blobs()

        for blob in blob_list:

            download_file_path = os.path.join(self.config["files"]["download-blob-directory"], blob.name)
            if not os.path.exists(download_file_path):
                print("\nDownloading blob to \n\t" + download_file_path)

                blob_client = self.blob_service_client.get_blob_client(
                    container=self.config["storage"]["container"], blob=blob.name)

                with open(download_file_path, "wb") as my_blob:
                    my_blob.writelines([blob_client.download_blob().readall()])

    def list_files_in_container(self, container, name_starts_with=None):
        """
        this method list all the files in a container
        :param container:
        :return:
        """
        container_client = self.blob_service_client.get_container_client(
            container
        )
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

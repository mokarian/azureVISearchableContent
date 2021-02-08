import json

from os import listdir, getenv
from os.path import isfile, exists, join

from utils.util import Util


class ClientAbstract(object):
    config = Util().config if exists("config/config.yml") else None

    @staticmethod
    def read_files_from_directory(path):
        files = [f for f in listdir(path) if isfile(join(path, f))]
        return files

    @staticmethod
    def read_file_from_directory(path):
        try:
            with open(path) as f:
                return json.load(f)
        except ValueError:
            print("could not read from the json file")

    def write_status_file(self, file, path):
        if self.config:
            out_path = join(self.config["files"]["processed-directory"], path)
        else:
            out_path = join(getenv("FILE_PROCESSING_LOGS_DIR"), path)
        with open(out_path, "a") as f:
            f.write(file + "\n")

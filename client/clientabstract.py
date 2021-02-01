import json
import os

from os import listdir
from os.path import isfile, join

from utils.util import Util


class ClientAbstract(object):
    config = Util().config

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
        full_path = os.path.join(self.config["files"]["processed-directory"], path)
        with open(full_path, 'a') as f:
            f.write(file + "\n")

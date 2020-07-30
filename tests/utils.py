import json
import os


class Utils:
    def read_json_from_resources(self, path, change_key_to_number=False):
        try:
            path = os.path.join("resources", path)
            with open(path) as f:

                json_file = json.load(f)
                if change_key_to_number:
                    json_file = self.convert_json_keys_to_int(json_file)
                return json_file
        except ValueError:
            print("could not read from the json file")

    @staticmethod
    def convert_json_keys_to_int(dict_with_string_keys):
        dict_with_int_keys = dict()
        for k, v in dict_with_string_keys.items():
            dict_with_int_keys[int(k)] = v
        return dict_with_int_keys

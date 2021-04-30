import re
import os
import glob
import json

def build_dependencies(category, operation_type, dependencies_file):
    found_dependencies = find_dependencies(category, operation_type)

def find_dependencies(category, operation_type):
    found = {
        "category": category,
        "name": operation_type,
        "last_push": {},
        "libraries": []
    }
    unopened = []

    directory_maps = load_directory_maps()
    directory_map = select(directory_maps, category, operation_type)
    unopened.append(directory_map)

    while unopened:
        filepaths = [get_filepath(d) for d in unopened]
        unopened = []

        for filepath in filepaths:
            for category, name in search_file(filepath):
                directory_map = select(directory_maps, category, name)
                if not directory_map:
                    msg = "Could not find pfish repository for {}/{}"
                    print(msg.format(category, name))
                    continue

                if not select(found["libraries"], category, name):
                    library = {
                        "category": category,
                        "name": name,
                        "last_push": {}
                    }
                    found["libraries"].append(library)

                if not select(unopened, category, name):
                    unopened.append(directory_map)

    return found

def search_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    needs = []
    pattern = re.compile(r'^\s*needs\s+[\"\'](.+)\/(.+)[\"\']')
    for l in lines:
        match = pattern.search(l)
        if match:
            needs.append((match.group(1), match.group(2)))
    return needs

def load_directory_maps():
    directory_maps = []
    for filepath in glob.iglob('**/definition.json', recursive=True):
        with open(filepath, 'r') as f:
            definiton = json.load(f)
        directory = {
            "name": definiton["name"],
            "category": definiton["category"],
            "parent_class": definiton["parent_class"],
            "directory": os.path.dirname(filepath)
        }
        directory_maps.append(directory)
    return directory_maps

def select(lst, category, name):
    selected = (x for x in lst if x["category"] == category and x["name"] == name)
    return next(selected, None)

def get_filepath(directory_map):
    parent_class = directory_map["parent_class"]
    if parent_class == "Library":
        filename = "source.rb"
    elif parent_class == "OperationType":
        filename = "protocol.rb"
    else:
        raise "Unrecognized parent class: {}".format(parent_class)
    return os.path.join(directory_map["directory"], filename)

if __name__ == "__main__":
    dependencies = find_dependencies("Yeast Display", "Challenge and Label")
    print(dependencies)


import re
import os
import glob
import json

def build_dependencies(category, operation_type, dependencies_file):
    found = find_dependencies(category, operation_type)
    all_existing = load_existing_dependencies(dependencies_file)

    # Split remove the relevant dependency object from all_existing
    existing = select(all_existing, category, operation_type)
    all_existing = remove(all_existing, category, operation_type)

    # Transfer the last_push objects from the existing JSON
    if existing:
        found["last_push"] = existing.get("last_push", {})
        for found_library in found["libraries"]:
            existing_library = select(existing["libraries"],
                                      found_library["category"],
                                      found_library["name"])
            if existing_library:
                found_library["last_push"] = existing_library.get("last_push", {})

    found["libraries"].sort(key=lambda x: (x["category"], x["name"]))

    # Recombine and save the file with updated dependencies
    all_existing.append(found)
    save_all_dependencies(all_existing, dependencies_file)


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

def remove(lst, category, name):
    return [x for x in lst if not (x["category"] == category and x["name"] == name)]

def get_filepath(directory_map):
    parent_class = directory_map["parent_class"]
    if parent_class == "Library":
        filename = "source.rb"
    elif parent_class == "OperationType":
        filename = "protocol.rb"
    else:
        raise "Unrecognized parent class: {}".format(parent_class)
    return os.path.join(directory_map["directory"], filename)

def load_existing_dependencies(dependencies_file):
    if os.path.exists(dependencies_file):
        with open(dependencies_file, 'r') as f:
            existing_dependencies = json.load(f)
        return existing_dependencies
    else:
        return []

def save_all_dependencies(all_dependencies, dependencies_file):
    with open(dependencies_file, 'w') as f:
        json.dump(all_dependencies, f, indent=2)

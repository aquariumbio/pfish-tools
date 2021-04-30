import os
import glob
import re
import json
import subprocess
import time
import pathlib

class DependencyManager():
    PFISH_CMD = "python3 ../script/pyfish.py"
    NEWLINE = "\n"

    def __init__(self, category, operation_type, dependencies_file, definitions):
        self.operation_type_category = category
        self.operation_type_name = operation_type
        self.definitions = definitions
        self.operation_type_directory = self.select_directory(self.operation_type_category,
                                                              self.operation_type_name)
        self.dependencies_file = dependencies_file
        self.all_dependencies = self.load_all_dependencies()
        self.dependencies = self.select_dependencies()
        self.pfish_default = self.get_pfish_default()

    def push_all_libraries(self, force):
        for dependency in self.dependencies["libraries"]:
            self.push_library(dependency, force)

    def push_library(self, dependency, force):
        if force or self.library_stale(dependency):
            category = dependency["category"]
            name = dependency["name"]
            msg = self.push_library_check_status(category, name)
            print(msg)
            self.add_dependency_timestamp(dependency)

    def push_library_check_status(self, category, name):
        directory = self.select_directory(category, name)
        msg = self.pfish_exec('push', directory)
        if self.library_push_status(msg, name) == 'created':
            msg = self.pfish_exec('push', directory)
        return msg

    # TODO: This is not working because the messages from are not being passed back
    def library_push_status(self, msg, name):
        report = msg.split(DependencyManager.NEWLINE)[2]
        if report.endswith(name):
            return 'complete'
        elif report.endswith("libraries.json"):
            return 'created'
        else:
            return 'error'

    def push_operation_type(self, force):
        if force or self.operation_type_stale():
            msg = self.pfish_exec('push', self.operation_type_directory)
            print(msg)
            self.add_operation_type_timestamp()

    def test_operation_type(self):
        msg = self.pfish_exec('test', self.operation_type_directory)
        print(msg)
        self.add_operation_type_timestamp()

    def pfish_exec(self, task, directory):
        cmd = "{} {} -d '{}'".format(DependencyManager.PFISH_CMD, task, directory)
        return self.subprocess_check_output(cmd)

    def add_dependency_timestamp(self, dependency):
        self.add_timestamp(dependency)

    def add_operation_type_timestamp(self):
        self.add_timestamp(self.dependencies)

    def add_timestamp(self, target):
        target["last_push"][self.pfish_default] = self.timestamp()
        self.save_all_dependencies()

    def timestamp(self):
        return time.time()

    def operation_type_stale(self):
        ptime = self.dependencies["last_push"].get(self.pfish_default)
        if not ptime: return True

        files = ["protocol.rb", "test.rb", "cost_model.rb", "documentation.rb", "precondition.rb"]
        for file in files:
            mtime = self.file_mtime(os.path.join(self.operation_type_directory, file))
            if mtime > ptime: return True

        return False

    def library_stale(self, dependency):
        directory = self.select_directory(dependency["category"], dependency["name"])
        mtime = self.file_mtime(os.path.join(directory, "source.rb"))
        ptime = dependency["last_push"].get(self.pfish_default)
        if ptime:
            return mtime > ptime
        else:
            return True

    def file_mtime(self, filename):
        fname = pathlib.Path(filename)
        assert fname.exists(), f'No such file: {filename}'
        return fname.stat().st_mtime

    def get_pfish_default(self):
        cmd = "{} configure show".format(DependencyManager.PFISH_CMD)
        msg = self.subprocess_check_output(cmd)
        return msg.split(DependencyManager.NEWLINE)[0].split(" ")[-1]

    def subprocess_check_output(self, cmd):
        msg = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return msg.decode("utf-8")

    def load_all_dependencies(self):
        with open(self.dependencies_file, 'r') as f:
            all_dependencies = json.load(f)
        return all_dependencies

    def save_all_dependencies(self):
        with open(self.dependencies_file, 'w') as f:
            json.dump(self.all_dependencies, f, indent=2)

    def select_dependencies(self):
        return self.select(self.all_dependencies, self.operation_type_category,
                           self.operation_type_name)

    def select_directory(self, category, name):
        return self.select(self.definitions, category, name).get("directory")

    def select(self, lst, category, name):
        selected = (x for x in lst if x["category"] == category and x["name"] == name)
        return next(selected, None)
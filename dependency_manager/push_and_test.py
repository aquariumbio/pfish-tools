from argparse import ArgumentParser
from dependency_manager import DependencyManager

def main():
    args = get_args()
    dependency_manager = DependencyManager(args.category, args.operation_type,
                                           args.dependencies_file)

    dependency_manager.set_pfish_default("laptop", "neptune",
                                         "aquarium", "http://localhost")

    dependency_manager.push_all_libraries(args.force)
    dependency_manager.push_operation_type(args.force)

def get_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dependencies_file",
                        help="the file containing dependencies to push before testing")
    parser.add_argument("-o", "--operation_type",
                        help="the operation type to push and test")
    parser.add_argument("-c", "--category",
                        help="category of the operation type")
    parser.add_argument("-f", "--force", action='store_true',
                        help="push all dependencies regardless of update time")
    return parser.parse_args()

if __name__ == "__main__":
    main()
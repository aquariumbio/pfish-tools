from argparse import ArgumentParser
from dependency_manager import DependencyManager

def main():
    args = get_args()
    dependency_manager = DependencyManager(
        args.category,
        args.operation_type,
        args.dependencies_file
    )

    dependency_manager.push_all_libraries()
    dependency_manager.push_operation_type()

def get_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dependencies_file",
                        help="the file containing dependencies to push before testing")
    parser.add_argument("-o", "--operation_type",
                        help="the operation type to push and test")
    parser.add_argument("-c", "--category",
                        help="category of the operation type")
    return parser.parse_args()

if __name__ == "__main__":
    main()

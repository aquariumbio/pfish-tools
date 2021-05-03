from argparse import ArgumentParser
from dependency_manager import DependencyManager
from dependency_builder import load_definitions, build_dependencies, default_dependencies_file

def main():
    args = get_args()

    definitions = load_definitions()
    build_dependencies(args.category, args.operation_type,
                       args.dependencies_file, definitions)

    if not args.build_only:
        dependency_manager = DependencyManager(args.category, args.operation_type,
                                               args.dependencies_file, definitions)

        dependency_manager.push_all_libraries(args.force)
        dependency_manager.push_operation_type(args.force)

def get_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dependencies_file", default=default_dependencies_file(),
                        help="the file containing dependencies to push before testing")
    parser.add_argument("-o", "--operation_type",
                        help="the operation type to push and test")
    parser.add_argument("-c", "--category",
                        help="category of the operation type")
    parser.add_argument("-f", "--force", action='store_true',
                        help="push all dependencies regardless of update time")
    parser.add_argument("-B", "--build_only", action='store_true',
                        help="rebuild the dependencies file but don't push or test")
    return parser.parse_args()

if __name__ == "__main__":
    main()

# pfish-tools
Tools for working with [pfish](https://github.com/aquariumbio/pfish)

## Format Test Results
The script `format_test_results.py` converts the `results.json` output of pfish into a human-readable markdown. To use it, simply copy it into a pfish repo and run `python3 format_test_results.py`. The script will find all `results.json` files in subdirectories and write the output `results.md` in the same location. 

## Push and Test Dependencies
`push-and-test` is a Dockerized app that manages dependencies for protocols. The dependency information is stored in a JSON file like this one:

```bash
[
  {
    "category": "Demo",            # OperationType
    "name": "Foo",
    "last_push": {},
    "libraries": [
      {
        "category": "Demo Libs",   # Library 1
        "name": "FooBar",
        "last_push": {}
      },
      {
        "category": "Demo Libs",   # Library 2
        "name": "FooBaz",
        "last_push": {}
      }
    ]
  }
]
```
where `Foo` is the OperationType and `FooBar` and `FooBaz` are Libraries that `Foo` depends on. The app will push all the files for the OperationType and its dependencies *only if they have been modified since the last push*.

### Installation
You should [install](https://github.com/aquariumbio/pfish#getting-started) and [configure](https://github.com/aquariumbio/pfish#configuring) pfish before installing or using this app.

```bash
git clone https://github.com/dvnstrcklnd/pfish-tools.git
cd pfish-tools
docker build -t push_and_test .
install -m 0755 push-and-test-wrapper ~/bin/push-and-test
```

### Usage
First, create a JSON like the one above that describes your dependencies. (Script to do this coming soon.) Place this file in the directory that contains your pfish repos:
```bash
`-- my_pfish_protocols
    |-- dependencies.json <<<
    |-- demo-repo
    |   |-- demo
    |   `-- demo_libs
    `-- another-repo
```
To run the app:
```bash
cd path/to/my_pfish_protocols
push-and-test -d dependencies.json -c 'Demo' -o 'Foo'
```
This will push the OperationType `Foo` and its dependencies. It will also record the push time for each push in `dependencies.json`. The next time you run the script, it will only push the files that have been saved since the last push. To push all regardless of whether they have been updated, use the `-f` flag:
```bash
push-and-test -d dependencies.json -c 'Demo' -o 'Foo' -f
```
**At this time you can only push based on the OperationType.** Use pfish for pushing individual Libraries. 

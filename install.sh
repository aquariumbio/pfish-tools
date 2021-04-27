#!/bin/sh
mkdir -p $HOME/bin
wget --directory-prefix=$HOME/bin https://raw.githubusercontent.com/dvnstrcklnd/pfish-tools/main/format_test_results.py
install -m 0755 $HOME/bin/format_test_results.py
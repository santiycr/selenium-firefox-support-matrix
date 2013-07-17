#!/usr/bin/env python

import os
import sys
import glob
import json

from prettytable import PrettyTable
from termcolor import colored

from lib.parse_version import parse_version


def print_matrix(result_matrix):
    ff_versions = sorted(result_matrix.keys(), key=int)
    sel_versions = set()
    for ff_version in ff_versions:
        for sv in result_matrix[ff_version].keys():
            sel_versions.add(sv)
    sel_versions = sorted(sel_versions, key=parse_version)
    x = PrettyTable()
    x.padding_width = 1  # One space between column edges and contents (default)
    x.add_column('sel \ ff', sel_versions)
    for ff_version in ff_versions:
        x.add_column(ff_version,
                     [get_simbol(result_matrix[ff_version].get(sel_version, '?'))
                      for sel_version in sel_versions])
    print x


def get_simbol(results):
    if results == '?':
        return colored('?', 'red')
    if results['worked']:
        if results['native']:
            return colored('Y', 'green')
        else:
            return colored('O', 'yellow')
    else:
        return colored('N', 'red')


if __name__ == '__main__':
    result_matrix = {}
    for results_path in glob.glob(os.path.join(sys.argv[1],
                                               '*results.json')):
        with open(results_path) as results_file:
            result = json.loads(results_file.read())
            for key in result:
                if not key in result_matrix:
                    result_matrix[key] = {}
                result_matrix[key].update(result[key])

    print_matrix(result_matrix)

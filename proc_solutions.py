""" Process Google Python class exercises

Check the solutions run correctly:

    python tools/proc_solutions.py check

Write the exercise files from the solutions:

    python tools/proc_solutions.py write
"""
# Copyright 2016 Matthew Brett
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0
from __future__ import print_function

import os
import sys
import re
from glob import glob
from os.path import join as pjoin, basename, isdir, abspath
from subprocess import check_call

# Extra command line parameters when executing some solution scripts
COMMAND_PARAMS = {
    'babynames.py': ['baby1990.html', 'baby1992.html', 'baby1994.html'],
    'mimic.py': ['small.txt'],
    'wordcount.py': ['--count', 'small.txt'],
    'copyspecial.py': ['solution'],
    'logpuzzle.py': ['animal_code.google.com'],
}


def find_exercises(exercise_dir):
    soln_dir = pjoin(exercise_dir, 'solution')
    py_files = glob(pjoin(soln_dir, "*.py"))
    return [(pjoin(exercise_dir, basename(py_file)), py_file)
            for py_file in py_files]


def process_solution(solution_contents):
    exercise_contents = []
    state = None
    for line in solution_contents.splitlines(True):
        sline = line.strip()
        if re.match(r"#+ LAB\(begin solution\)", sline):
            state = 'solution'
        elif re.match(r"#+ LAB\(replace solution\)", sline):
            state = 'replace'
        elif re.match(r"#+ LAB\(end solution\)", sline):
            state = None
        elif state != 'solution':
            if state == 'replace':
                line = re.sub(r"#\s*", '', line)
            exercise_contents.append(line)
    return ''.join(exercise_contents)


def write_solution(solution_fname, exercise_fname):
    with open(solution_fname, 'rt') as fobj:
        solution = fobj.read()
    exercise = process_solution(solution)
    with open(exercise_fname, 'wt') as fobj:
        fobj.write(exercise)


def rewrite_exercise_dir(exercise_dir):
    for exercise_fname, solution_fname in find_exercises(exercise_dir):
        write_solution(solution_fname, exercise_fname)


def exercise_sdirs(start_path):
    sdirs = []
    for path in os.listdir(start_path):
        full_path = pjoin(start_path, path)
        if isdir(full_path) and isdir(pjoin(full_path, 'solution')):
            sdirs.append(full_path)
    return sdirs


def check_solutions(exercise_dir):
    for exercise_fname, solution_fname in find_exercises(exercise_dir):
        check_solution(exercise_dir, solution_fname)


def check_solution(exercise_dir, solution_fname):
    print('Checking ' + solution_fname)
    fname = abspath(solution_fname)
    cwd = os.getcwd()
    # Allow for commands that need parameters
    parameters = COMMAND_PARAMS.get(basename(fname), [])
    try:
        os.chdir(exercise_dir)
        check_call([sys.executable, fname] + parameters)
    finally:
        os.chdir(cwd)


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'check'
    start_path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    if command == 'write':
        for exercise_dir in exercise_sdirs(start_path):
            rewrite_exercise_dir(exercise_dir)
    elif command == 'check':
        for exercise_dir in exercise_sdirs(start_path):
            check_solutions(exercise_dir)
        check_solution(start_path, 'hello.py')
    else:
        raise RuntimeError('Invalid command ' + command)


if __name__ == '__main__':
    main()

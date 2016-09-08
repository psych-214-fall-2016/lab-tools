""" Process Google Python class exercises

Check the solutions run correctly:

    python tools/proc_solutions.py check

Write the exercise files from the solutions:

    python tools/proc_solutions.py write

Script assumes directory structure:

    exercise_name/an_exercise.py  <- generated by "write"
                 /another_exercise.py  <- generated by "write"
                 /solution/an_exercise.py
                 /solution/another_exercise.py
                 /solution/another_exercise.params

"another_exercise.params" is a Python syntax file with a single expression
returning a list of parameters to pass when running ``another_exercise.py``
from the ``exercise_name`` directory.  The script uses these for the "check"
action.  For example, imagine ``another_exercise.params`` contains this::

    # Default parameters for running "another_exercise.py"
    ['some_file.txt']

Then the resulting test with "check" will run the equivalent of::

    cd exercise_name
    python solution/another_exercise.py some_file.txt

Use a list of lists in the parameter file to run more than one check::

    # Default parameters for running "another_exercise.py" twice
    ['some_file.txt', 'another_file.txt']

That results in the equivalent of::

    cd exercise_name
    python solution/another_exercise.py some_file.txt
    python solution/another_exercise.py another_file.txt
"""
# Copyright 2016 Matthew Brett
# Licensed under the 2-clause BSD license.  See LICENSE file.

from __future__ import print_function

import os
import sys
import re
from glob import glob
from os.path import join as pjoin, basename, isdir, isfile, abspath, splitext
from subprocess import check_call
from ast import literal_eval


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


def get_params(solution_fname):
    """ Get extra parameters for running solution

    Parameters
    ----------
    solution_fname : str
        Path to solution ".py" file

    Returns
    -------
    params_list : list of lists
        List of lists where each list contains a sequence of strings that will
        be passed to the script on the command line.
    """
    params_fname = splitext(solution_fname)[0] + '.params'
    if not isfile(params_fname):
        return [[]]
    with open(params_fname, 'rt') as fobj:
        contents = fobj.read()
    params = literal_eval(contents)
    # Parameters should be list, or list of lists
    return params if isinstance(params[0], list) else [params]


def check_solution(exercise_dir, solution_fname):
    print('Checking ' + solution_fname)
    fname = abspath(solution_fname)
    cwd = os.getcwd()
    # Allow for commands that need parameters
    parameters = get_params(solution_fname)
    try:
        os.chdir(exercise_dir)
        for params in parameters:
            check_call([sys.executable, fname] + params)
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

""" Tests for string fill functions
"""

from os.path import abspath, dirname, join as pjoin
import sys

CODE_DIR = abspath(pjoin(dirname(__file__), '..'))

sys.path.append(CODE_DIR)

from proc_solutions import format_values, process_config


def test_fill_dict_strings():
    assert format_values({}, {}) == {}
    assert format_values([], {}) == []
    assert format_values(1, {}) == 1
    assert format_values(1.2, {}) == 1.2
    assert format_values('foo', {}) == 'foo'
    assert format_values('foo{bar}', {'bar': 'baz'}) == 'foobaz'
    assert format_values({'foo': 'bar'}, {}) == {'foo': 'bar'}
    ns = {'baz': 'zorg', 'jessie': 'pingu'}
    assert (format_values({'foo': 'bar{baz}'}, ns)
            == {'foo': 'barzorg'})
    assert (format_values({'root': [1, 'b{baz}']}, ns) ==
            {'root': [1, 'bzorg']})
    assert (format_values({'root': {1: 'b{baz}'}}, ns) ==
            {'root': {1: 'bzorg'}})
    assert (format_values({'root': {1: {2: 'b{baz}'}}}, ns) ==
            {'root': {1: {2: 'bzorg'}}})


def test_fill_config():
    raw_config = {
        'solution_dir': 'foo',
        'solution':
        {'babynames': {'checks': [{'command': ['{sys_exe}',
                                               '{in_path}',
                                               'baby1990.html',
                                               'baby1992.html',
                                               'baby1994.html']}]},
         'wordcount': {'checks': [{'command': ['{sys_exe}',
                                               '{in_path}',
                                               '--count',
                                               'small.txt']},
                                  {'command': ['{sys_exe}',
                                               '{in_path}',
                                               '--topcount', 'alice.txt']
                                  }
                                 ]
                      }
        }
    }
    p_config = process_config(raw_config)
    foo_dir = pjoin(CODE_DIR, 'foo')
    assert (p_config == {
        'solution_dir': 'foo',
        'solution': {
            'babynames': {
                'out_path': pjoin(CODE_DIR, 'babynames.py'),
                'checks': [
                    {'cwd': CODE_DIR,
                    'command': [
                        sys.executable,
                        pjoin(foo_dir, 'babynames.py'),
                        'baby1990.html',
                        'baby1992.html',
                        'baby1994.html']}],
                'in_path': pjoin(foo_dir, 'babynames.py')},
            'wordcount': {
                'out_path': pjoin(CODE_DIR, 'wordcount.py'),
                'checks': [
                    {'cwd': CODE_DIR,
                    'command': [
                        sys.executable,
                        pjoin(foo_dir, 'wordcount.py'),
                        '--count',
                        'small.txt']},
                    {'cwd': CODE_DIR,
                    'command': [
                        sys.executable,
                        pjoin(foo_dir, 'wordcount.py'),
                        '--topcount',
                        'alice.txt']}],
                'in_path': pjoin(foo_dir, 'wordcount.py')}
        }})

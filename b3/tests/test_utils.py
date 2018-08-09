from b3.utils import thread, threadm, deepmerge

def test_thread():
    expected = '3'
    inc = lambda v: v + 1
    assert expected == thread(1, inc, inc, str)

def test_threadm():
    "if given a tuple of values, threadm will apply the pipeline to each value"
    expected = '3'
    inc = lambda v: v + 1
    assert (expected, expected) == threadm((1, 1), inc, inc, str)

def test_deepmerge():
    cases = [
        # basic dicts
        (({}, {}), {}),
        (({'a': 1}, {}), {'a': 1}),
        (({'a': 1}, {'a': 2}), {'a': 2}),
        (({}, {'a': 1}), {'a': 1}),

        # basic lists
        (([], []), []),
        (([1], []), [1]),
        (([1], [1]), [1, 1]),
        (([1], [1, 2]), [1, 1, 2]),

        # mixing lists and scalar
        (([1, 2], 3),
         [1, 2, 3]), # b is 'merged' (appended) into a

        ((1, [2]),
         [2]), # b cannot be merged into a, so b replaces a
        
        # deep dicts
        (({'a': {'b': 3, 'c': 5}}, {'a': {'b': 4}}),
          {'a': {'b': 4, 'c': 5}}),

        # deep lists
        (([1, [2, [3]]], [4]), [1, [2, [3]], 4]), # extend
        (([1, 2], 3), [1, 2, 3]), # append

        # mixed deep dicts and lists
        (({'a': {'b': [1], 'c': [2], 'd': 3}}, {'a': {'b': [2], 'c': [2], 'd': 4}}), # merge, append, extend, replace
          {'a': {'b': [1, 2], 'c': [2, 2], 'd': 4}}),

        (({"r": [{"foo": "bar"}], "o": []}, {"r": [{"bar": "baz"}]}),
          {"r": [{"foo": "bar"}, {"bar": "baz"}], "o": []}),
    ]
    for args, expected in cases:
        assert expected == deepmerge(*args), "failed. expecting: %s" % expected

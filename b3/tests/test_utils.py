from b3.utils import thread, threadm

def test_thread():
    expected = '3'
    inc = lambda v: v + 1
    assert expected == thread(1, inc, inc, str)

def test_threadm():
    "if given a tuple of values, threadm will apply the pipeline to each value"
    expected = '3'
    inc = lambda v: v + 1
    assert (expected, expected) == threadm((1, 1), inc, inc, str)

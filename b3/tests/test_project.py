from b3 import project
from b3.utils import BldrAssertionError
import pytest

def test_mkiid():
    cases = [
        (['foo', 'bar'], 'foo--bar'),
        ([' foo ', 'bar'], 'foo--bar'),
        (['foo', ' bar '], 'foo--bar'),
        ([' foo ', ' bar '], 'foo--bar'),
    ]
    for args, expected in cases:
        assert expected == project.mkiid(*args)

def test_mkiid_bad():
    cases = [
        ('foo', ' '),
        (' ', 'bar'),
        (' ', ' '),
    ]
    for args in cases:
        with pytest.raises(BldrAssertionError):
            project.mkiid(*args)

def test_basic_project_defaults():
    expected = {
        'resource1': {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []}
    }
    actual = project.project_data('basic-defaults', oname='test-project')
    assert expected == actual

def test_basic_project_overrides():
    expected = {
        'resource1': {'type': 'vm', 'os': 'ubuntu-18.04', 'size': 'huge', 'extra-volumes': []}
    }
    actual = project.project_data('basic-overrides', oname='test-project')
    assert expected == actual

def test_basic_project_multi_resources():
    expected = {
        'resource1': {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []},
        'resource2': {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []}
    }
    actual = project.project_data('basic-multi-resources', oname='test-project')
    assert expected == actual
    
def test_basic_project_multi_resources_overrides():
    expected = {
        'resource1': {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []},
        'resource2': {'type': 'vm', 'os': 'ubuntu-18.04', 'size': 'huge', 'extra-volumes': []}
    }
    actual = project.project_data('basic-multi-resources-w-overrides', oname='test-project')
    assert expected == actual

def test_basic_project_extended_defaults():
    expected = {
        'resource1': {
            'type': 'vm',
            'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': [
                {
                    'type': 'extra-volume',
                    'size': 10,
                    'dev': '/dev/xvdh',
                    'mnt': '/mnt/xvdh'
                }
            ]
        }
    }
    actual = project.project_data('basic-defaults-extended', oname='test-project')
    assert expected == actual

def test_basic_project_extended_defaults_overrides():
    expected = {
        'resource1': {
            'type': 'vm',
            'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': [
                {
                    'type': 'extra-volume',
                    'size': 100,
                    'dev': '/dev/xvdh',
                    'mnt': '/foo/bar'
                }
            ]
        }
    }
    actual = project.project_data('basic-defaults-extended-w-overrides', oname='test-project')
    assert expected == actual

def test_project_extended_defaults():
    expected = {
        'resource1': {
            'type': 'vm',
            'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': [
                {
                    'type': 'extra-volume',
                    'size': 10,
                    'dev': '/dev/xvda',
                    'mnt': '/mnt/xvdh',
                },
                {
                    'type': 'extra-volume',
                    'size': 10,
                    'dev': '/dev/xvdh',
                    'mnt': '/mnt/xvdb',
                },
                {
                    'type': 'extra-volume',
                    'size': 100,
                    'dev': '/dev/xvdh',
                    'mnt': '/mnt/xvdh'
                }
            ]
        }
    }
    actual = project.project_data('extended-defaults', oname='test-project-2')
    assert expected == actual

def test_project_extended_defaults_overrides():
    expected = {
        'resource1': {
            'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': []
        }
    }
    actual = project.project_data('extended-defaults-w-overrides', oname='test-project-2')
    assert expected == actual

def test_basic_project_extended_defaults_overrides2():
    expected = {
        'resource1': {
            'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': [
                {
                    'type': 'extra-volume',
                    'size': 10,
                    'dev': '/dev/xvdh',
                    'mnt': '/mnt/xvdh'
                }
            ]
        }
    }
    actual = project.project_data('extended-defaults-w-overrides2', oname='test-project-2')
    assert expected == actual

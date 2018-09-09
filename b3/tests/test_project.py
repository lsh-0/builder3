from b3 import conf, project
from b3.utils import BldrAssertionError
import pytest
from unittest.mock import patch

def test_mk_iid():
    cases = [
        (['foo', 'bar'], 'foo--bar'),
        ([' foo ', 'bar'], 'foo--bar'),
        (['foo', ' bar '], 'foo--bar'),
        ([' foo ', ' bar '], 'foo--bar'),
    ]
    for args, expected in cases:
        assert expected == project.mk_iid(*args)

def test_mk_iid_bad():
    cases = [
        ('foo', ' '),
        (' ', 'bar'),
        (' ', ' '),
    ]
    for args in cases:
        with pytest.raises(BldrAssertionError):
            project.mk_iid(*args)

def test_basic_project_defaults():
    expected = [
        {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []}
    ]
    actual = project.project_data('basic-defaults', oname='test-project')
    assert expected == actual

def test_basic_project_overrides():
    expected = [
        {'type': 'vm', 'os': 'ubuntu-18.04', 'size': 'huge', 'extra-volumes': []}
    ]
    actual = project.project_data('basic-overrides', oname='test-project')
    assert expected == actual

def test_basic_project_multi_resources():
    expected = [
        {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []},
        {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []}
    ]
    actual = project.project_data('basic-multi-resources', oname='test-project')
    assert expected == actual

def test_basic_project_multi_resources_overrides():
    expected = [
        {'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny', 'extra-volumes': []},
        {'type': 'vm', 'os': 'ubuntu-18.04', 'size': 'huge', 'extra-volumes': []}
    ]
    actual = project.project_data('basic-multi-resources-w-overrides', oname='test-project')
    assert expected == actual

def test_basic_project_extended_defaults():
    expected = [
        {
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
    ]
    actual = project.project_data('basic-defaults-extended', oname='test-project')
    assert expected == actual

def test_basic_project_extended_defaults_overrides():
    expected = [
        {
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
    ]
    actual = project.project_data('basic-defaults-extended-w-overrides', oname='test-project')
    assert expected == actual

def test_project_extended_defaults():
    expected = [
        {
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
    ]
    actual = project.project_data('extended-defaults', oname='test-project-2')
    assert expected == actual

def test_project_extended_defaults_overrides():
    expected = [
        {
            'type': 'vm', 'os': 'ubuntu-16.04', 'size': 'tiny',
            'extra-volumes': []
        }
    ]
    actual = project.project_data('extended-defaults-w-overrides', oname='test-project-2')
    assert expected == actual

def test_basic_project_extended_defaults_overrides2():
    expected = [
        {
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
    ]
    actual = project.project_data('extended-defaults-w-overrides2', oname='test-project-2')
    assert expected == actual

def test_instance_list_when_instance_dir_dne():
    "don't die when the instance dir doesn't exist"
    with patch('b3.conf.INSTANCE_DIR', '/foo/bar'):
        assert project.instance_list() == []

def test_instance_list_when_instance_dir_noisy():
    "instance directories look a certain way, ensure anything that doesn't look like one is filtered out"
    with patch('b3.conf.INSTANCE_DIR', conf.PROJECT_DIR):
        assert project.instance_list() == []

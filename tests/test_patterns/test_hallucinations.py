"""Tests for hallucination detection patterns."""

import pytest
from pathlib import Path

from sloppy.detector import Detector


def test_mutable_default_list_detected(tmp_python_file):
    """Test that mutable list defaults are detected."""
    code = '''
def bad_func(items=[]):
    items.append(1)
    return items
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    mutable_issues = [i for i in issues if i.pattern_id == "mutable_default_arg"]
    assert len(mutable_issues) == 1
    assert mutable_issues[0].severity.value == "critical"


def test_mutable_default_dict_detected(tmp_python_file):
    """Test that mutable dict defaults are detected."""
    code = '''
def bad_func(config={}):
    config['key'] = 'value'
    return config
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    mutable_issues = [i for i in issues if i.pattern_id == "mutable_default_arg"]
    assert len(mutable_issues) == 1


def test_none_default_not_flagged(tmp_python_file):
    """Test that None defaults are not flagged."""
    code = '''
def good_func(items=None):
    if items is None:
        items = []
    return items
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    mutable_issues = [i for i in issues if i.pattern_id == "mutable_default_arg"]
    assert len(mutable_issues) == 0


def test_pass_placeholder_detected(tmp_python_file):
    """Test that pass placeholders are detected."""
    code = '''
def placeholder_func():
    pass
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    pass_issues = [i for i in issues if i.pattern_id == "pass_placeholder"]
    assert len(pass_issues) == 1


def test_ellipsis_placeholder_detected(tmp_python_file):
    """Test that ellipsis placeholders are detected."""
    code = '''
def placeholder_func():
    ...
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    ellipsis_issues = [i for i in issues if i.pattern_id == "ellipsis_placeholder"]
    assert len(ellipsis_issues) == 1


def test_notimplemented_placeholder_detected(tmp_python_file):
    """Test that NotImplementedError placeholders are detected."""
    code = '''
def placeholder_func():
    raise NotImplementedError()
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    not_impl_issues = [i for i in issues if i.pattern_id == "notimplemented_placeholder"]
    assert len(not_impl_issues) == 1


def test_real_implementation_not_flagged(tmp_python_file):
    """Test that real implementations are not flagged as placeholders."""
    code = '''
def real_func(x):
    result = x * 2
    return result
'''
    file = tmp_python_file(code)
    detector = Detector()
    issues = detector.scan([file])
    
    placeholder_ids = {"pass_placeholder", "ellipsis_placeholder", "notimplemented_placeholder"}
    placeholder_issues = [i for i in issues if i.pattern_id in placeholder_ids]
    assert len(placeholder_issues) == 0

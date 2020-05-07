# Python
from __future__ import unicode_literals
import functools


# From: http://stackoverflow.com/questions/9882280/find-out-if-a-function-has-been-called
def trackcalls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)
    wrapper.has_been_called = False
    return wrapper

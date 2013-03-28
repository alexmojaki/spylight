#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes

from inspect import isclass
from threading import _active, Event, Thread


def _async_raise(tid, exception):
    if not isclass(exception):
        raise TypeError('Only types or classes can be raised (not instances)')
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.
                                                     py_object(exception))
    if res == 0:
        raise RuntimeError('Thread currently not alive or invalid thread \
identifier')
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble, and you
        # should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError('PyThreadState_SetAsyncExc failed')


class ThreadExit(BaseException):
    pass


class StoppableThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super(StoppableThread, self).__init__(group, target, name, args,
                                              kwargs)
        self._stop = Event()

    def is_stopped(self):
        return self._stop.is_set()

    def stop(self, force=False):
        self._stop.set()

        if force:
            for tid, tobj in _active.items():
                if tobj is self:
                    _async_raise(tid, ThreadExit)
                    return

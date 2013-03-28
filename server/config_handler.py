#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser as ConfigParser


class ConfigHandler(object):
    def __init__(self, filename, defaults={}, types={}):
        self._section_cache = {}
        self._types = types
        self._config_parser = ConfigParser(defaults)
        self._config_parser.read(filename)

    def __getattribute__(self, name):
        if name[0] == '_':
            return object.__getattribute__(self, name)
        if name not in object.__getattribute__(self, '_section_cache'):
            for s in object.__getattribute__(self,
                                             '_config_parser').sections():
                if object.__getattribute__(self, '_config_parser').has_option(
                        s, name):
                    object.__getattribute__(self, '_section_cache')[name] = s
                    break
            if name not in object.__getattribute__(self, '_section_cache'):
                object.__getattribute__(self, '_section_cache')[name] = None
        if object.__getattribute__(self, '_section_cache')[name] is not None:
            if name in object.__getattribute__(self, '_types'):
                if object.__getattribute__(self, '_types')[name] == int:
                    return object.__getattribute__(self,
                                                   'config_parser').getint(
                                                       object.__getattribute__(
                                                           self,
                                                           '_section_cache')
                                                       [name], name)
                elif object.__getattribute__(self, '_types')[name] == float:
                    return object.__getattribute__(self,
                                                   '_config_parser').getfloat(
                                                       object.__getattribute__(
                                                           self,
                                                           '_section_cache')
                                                       [name], name)
                elif object.__getattribute__(self, '_types')[name] == bool:
                    return object.__getattribute__(self, '_config_parser').\
                        getboolean(object.__getattribute__(
                            self, '_section_cache')[name], name)
                elif object.__getattribute__(self, '_types')[name] == str:
                    return object.__getattribute__(self, '_config_parser').get(
                        object.__getattribute__(self, '_section_cache')[name],
                        name)
                else:
                    raise ValueError('Type must be one of the following: int, \
float, bool or str')
            else:
                return object.__getattribute__(self, '_config_parser').get(
                    object.__getattribute__(self, '_section_cache')[name],
                    name)
        else:
            return AttributeError("'{}' object has no attribute '{}'".format(
                object.__getattribute__(self, '__name__'), name))

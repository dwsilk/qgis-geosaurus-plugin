# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractSpatialFunction(object):
    """
    Abstract Base Class defining the interface for a Spatial Function
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @classmethod
    @abstractproperty
    def function_name(self):
        pass

    @classmethod
    @abstractproperty
    def function_group(self):
        pass

    @classmethod
    @abstractproperty
    def function_help(self):
        pass

    @classmethod
    @abstractproperty
    def start_postgis_version(self):
        pass

    @classmethod
    @abstractproperty
    def spatial_type_support(cls):
        pass

    @classmethod
    @abstractproperty
    def return_type(self):
        pass

    @abstractmethod
    def execute_query(self):
        pass

    @abstractmethod
    def sample_query_as_text(self):
        pass

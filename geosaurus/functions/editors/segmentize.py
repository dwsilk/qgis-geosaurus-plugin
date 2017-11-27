# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class Segmentize(AbstractSpatialFunction):
    """
    ST_Segmentize
    """

    def __init__(self, max_segment_length=0):
        self._max_segment_length = max_segment_length

    @property
    def max_segment_length(self):
        return self._max_segment_length

    @max_segment_length.setter
    def max_segment_length(self, value):
        self._max_segment_length = value

    @classmethod
    def function_name(cls):
        return "ST_Segmentize"

    @classmethod
    def alias_name(cls):
        return None

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_Segmentize.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.2.2"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.GEOGRAPHY,
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        output = db.execute("""
            SELECT ST_AsText(ST_Segmentize(ST_GeomFromText(%s), %s));
        """, (wkt, self.max_segment_length, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_Segmentize(ST_GeomFromText('{0}'), {1}))
        """.format(wkt, self.max_segment_length)

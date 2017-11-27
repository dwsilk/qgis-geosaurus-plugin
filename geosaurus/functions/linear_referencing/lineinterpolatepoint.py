# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class LineInterpolatePoint(AbstractSpatialFunction):
    """
    ST_LineInterpolatePoint
    """

    def __init__(self, fraction=0):
        self._fraction = fraction

    @property
    def fraction(self):
        return self._fraction

    @fraction.setter
    def fraction(self, value):
        self._fraction = value

    @classmethod
    def function_name(cls):
        return "ST_LineInterpolatePoint"

    @classmethod
    def alias_name(cls):
        return [
            "ST_Line_Interpolate_Point", "2.0.x"
        ]

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_LineInterpolatePoint.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.1.1"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.HAS_Z_OR_M,
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        output = db.execute("""
            SELECT ST_AsText(ST_LineInterpolatePoint(ST_GeomFromText(%s), %s));
        """, (wkt, self.fraction, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_LineInterpolatePoint(ST_GeomFromText('{0}'), {1:.2f}))
        """.format(wkt, self.fraction, )

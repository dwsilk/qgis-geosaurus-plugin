# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class AddPoint(AbstractSpatialFunction):
    """
    ST_AddPoint
    """

    def __init__(self, point_x=0, point_y=0, position=0):
        self._point_x = point_x
        self._point_y = point_y
        self._position = position

    @property
    def point_x(self):
        return self._point_x

    @point_x.setter
    def point_x(self, value):
        self._point_x = value

    @property
    def point_y(self):
        return self._point_y

    @point_y.setter
    def point_y(self, value):
        self._point_y = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @classmethod
    def function_name(cls):
        return "ST_AddPoint"

    @classmethod
    def alias_name(cls):
        return None

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_AddPoint.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.1.0"

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
            SELECT ST_AsText(ST_AddPoint(ST_GeomFromText(%s), ST_MakePoint(%s, %s), %s));
        """, (wkt, self.point_x, self.point_y, self.position, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_Scale(ST_GeomFromText('{0}'), ST_MakePoint({1:.2f}, {2:.2f}), {3})
        """.format(wkt, self.point_x, self.point_y, self.position, )
